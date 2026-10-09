"""Deterministic preference ranking for ZAVRA's existing Shopify variants."""
from pathlib import Path
import pickle

HERE = Path(__file__).resolve().parent

def load_model(path=None):
    # Never unpickle user-supplied files: pickle can run arbitrary Python code.
    with open(path or HERE / 'zavra_recommender.pkl', 'rb') as f:
        model = pickle.load(f)
    if model.get('version') != 1 or not isinstance(model.get('variants'), list):
        raise ValueError('Unsupported recommender snapshot')
    return model

def norm(s):
    return str(s or '').strip().casefold()

def match_occasion(query, occasion):
    # Catalog descriptions use 'business meetings', 'formal events', etc.
    aliases = {'business meeting': 'business meetings', 'formal': 'formal events',
               'everyday': 'everyday smart wear', 'casual': 'everyday smart wear'}
    q = aliases.get(query, query)
    return bool(q) and q in occasion

def recommend(model, *, budget, size, color='Any', fabric='Any', occasion='Any', limit=3):
    active = [(field, model['weights'][field], norm(value)) for field, value in
              [('fabric', fabric), ('color', color), ('occasion', occasion)] if norm(value) not in ('', 'any')]
    denominator = sum(weight for _, weight, _ in active)
    unique = {}
    for row in model['variants']:
        if norm(row.get('available')) not in ('true', '1', 'yes', 'available'):
            continue
        try:
            price = float(row['price_bdt'])
        except (ValueError, TypeError, KeyError):
            continue
        if price > budget or (norm(size) not in ('', 'any') and norm(row.get('size')) != norm(size)):
            continue
        hits = []
        for field, weight, preference in active:
            value = norm(row.get('fabric_type' if field == 'fabric' else field))
            if ((field == 'occasion' and match_occasion(preference, value)) or
                (field == 'fabric' and (preference == value or preference == 'micro' and value == 'chinese micro')) or
                (field == 'color' and preference == value)):
                hits.append((field, weight))
        score = round(sum(weight for _, weight in hits) / denominator * 100, 1) if denominator else None
        product = {
            'product_id': row['product_id'], 'variant_id': row['variant_id'],
            'name': row['product_name'], 'fabric': row['fabric_type'],
            'color': row['color'], 'size': row['size'], 'sleeve_length': row.get('sleeve_length', ''),
            'price_bdt': price, 'original_price_bdt': float(row['original_price_bdt']) if row.get('original_price_bdt') else None,
            'available': True, 'match_score': score,
            'matched_preferences': [field for field, _ in hits],
            'image_url': row.get('image_url', ''), 'product_url': row.get('product_url', ''),
        }
        # Requesting 'Any' size still yields one result per Shopify product.
        key = row['product_id']
        if key not in unique or (product['match_score'] or 0) > (unique[key]['match_score'] or 0):
            unique[key] = product
    return sorted(unique.values(), key=lambda p: (-(p['match_score'] or 0), p['price_bdt'], p['name'], p['color']))[:limit]
