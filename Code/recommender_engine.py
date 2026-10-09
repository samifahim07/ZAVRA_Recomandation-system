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

def recommend(model, *, budget, size, color='Any', fabric='Any', occasion='Any', limit=None):
    """Strict filters first; optional occasion preference only ranks remaining items.

    Any means do not filter. Never recommend a different fabric/color as a fallback.
    """
    wanted_size, wanted_color, wanted_fabric = norm(size), norm(color), norm(fabric)
    wanted_occasion = norm(occasion)
    unique = {}
    for row in model['variants']:
        if norm(row.get('available')) not in ('true', '1', 'yes', 'available'):
            continue
        try:
            price = float(row['price_bdt'])
        except (ValueError, TypeError, KeyError):
            continue
        if price > budget:
            continue
        if wanted_size not in ('', 'any') and norm(row.get('size')) != wanted_size:
            continue
        if wanted_color not in ('', 'any') and norm(row.get('color')) != wanted_color:
            continue
        actual_fabric = norm(row.get('fabric_type'))
        if wanted_fabric not in ('', 'any') and not (
            actual_fabric == wanted_fabric or
            (wanted_fabric in ('micro', 'micro fabric') and actual_fabric == 'chinese micro')
        ):
            continue
        if wanted_occasion not in ('', 'any') and not match_occasion(wanted_occasion, norm(row.get('occasion'))):
            continue
        matched = [field for field, wanted in [('fabric', wanted_fabric), ('color', wanted_color),
                    ('occasion', wanted_occasion)] if wanted not in ('', 'any')]
        product = {
            'product_id': row['product_id'], 'variant_id': row['variant_id'],
            'name': row['product_name'], 'fabric': row['fabric_type'],
            'color': row['color'], 'size': row['size'], 'sleeve_length': row.get('sleeve_length', ''),
            'price_bdt': price,
            'original_price_bdt': float(row['original_price_bdt']) if row.get('original_price_bdt') else None,
            'available': True, 'match_score': 100.0 if matched else None,
            'matched_preferences': matched,
            'image_url': row.get('image_url', ''), 'product_url': row.get('product_url', ''),
        }
        # One result per product, not one per size variant. For Any size, prefer M for display.
        key = str(row['product_id'])
        if key not in unique or (wanted_size in ('', 'any') and norm(row.get('size')) == 'm'):
            unique[key] = product
    results = sorted(unique.values(), key=lambda item: (item['price_bdt'], item['fabric'], item['color']))
    return results[:limit] if limit is not None else results
