"""ZAVRA — beginner-friendly, stock-aware shirt recommender.
Run: python zavra_recommender.py
Uses the CSV files in the same folder; no third-party packages required.
"""
import csv
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
VARIANTS_FILE = HERE / 'ZAVRA_All_Shirts_Variants.csv'
PRODUCTS_FILE = HERE / 'ZAVRA_All_Shirts_Products.csv'


def load_csv(path):
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def clean(value):
    return str(value or '').strip().casefold()


def is_available(value):
    return clean(value) in ('true', 'yes', '1', 'available')


def recommend(budget, size, color='Any', fabric='Any', occasion='Any', top_n=3):
    """Hard filters: availability, maximum budget, size.
    Preferences: fabric 45%, color 40%, occasion 15% (if specified).
    When no preference specified, prioritize lower price.
    """
    rows = load_csv(VARIANTS_FILE)
    candidates = {}
    wanted_color, wanted_fabric, wanted_occasion = map(clean, (color, fabric, occasion))
    preferences = [(wanted_fabric, 45, 'fabric_type'), (wanted_color, 40, 'color'),
                   (wanted_occasion, 15, 'occasion')]
    active_weight = sum(w for val, w, _ in preferences if val not in ('', 'any'))
    for r in rows:
        if not is_available(r['available']):
            continue
        try:
            price = float(r['price_bdt'])
        except (ValueError, TypeError):
            continue
        if price > budget or (clean(size) not in ('', 'any') and clean(r['size']) != clean(size)):
            continue
        matches = 0
        reasons = []
        for val, weight, field in preferences:
            if val in ('', 'any'):
                continue
            found = val in clean(r[field]) if field == 'occasion' else val == clean(r[field])
            if found:
                matches += weight
                reasons.append({'fabric_type': 'Fabric', 'color': 'Color', 'occasion': 'Occasion'}[field])
        score = round(100 * matches / active_weight, 1) if active_weight else None
        entry = dict(r)
        entry['price'] = price
        entry['match_score'] = score
        entry['matched_preferences'] = ', '.join(reasons)
        # One result per shirt rather than one per size variant.
        key = r['product_id']
        if key not in candidates or (score or 0) > (candidates[key]['match_score'] or 0):
            candidates[key] = entry

    result = list(candidates.values())
    result.sort(key=lambda r: (-(r['match_score'] or 0), r['price'], r['product_name']))
    return result[:top_n]


def overview():
    products, variants = load_csv(PRODUCTS_FILE), load_csv(VARIANTS_FILE)
    print('ZAVRA inventory snapshot (source updated 2026-10-09)')
    print('Products:', len(products), '| Variants:', len(variants))
    print('Available variants:', sum(is_available(r['available']) for r in variants))
    print('Fabric counts:', dict(Counter(p['fabric_type'] for p in products)))
    print('Available sizes:', dict(Counter(r['size'] for r in variants if is_available(r['available']))))
    print('Price range (BDT):', min(float(p['price_bdt']) for p in products), '-', max(float(p['price_bdt']) for p in products))


def prompt_choice(name, default):
    value = input(f'{name} [{default}]: ').strip()
    return value or default


if __name__ == '__main__':
    overview()
    print('\nFind your top 3 available shirts. Press Enter to accept defaults.\n')
    try:
        budget = float(prompt_choice('Maximum budget in BDT', '800'))
        size = prompt_choice('Size (M / L / XL)', 'M')
        color = prompt_choice('Color (e.g. Black, White, Deep Maroon, Any)', 'Any')
        fabric = prompt_choice('Fabric (Bamboo / Cross / Chinese Micro / Any)', 'Any')
        occasion = prompt_choice('Occasion (Office / Formal / Everyday smart wear / Any)', 'Any')
        picks = recommend(budget, size, color, fabric, occasion)
        if not picks:
            print('\nNo in-stock shirts fit your budget and selected size. Try another size or budget.')
        else:
            print('\nTOP RECOMMENDATIONS')
            for idx, r in enumerate(picks, 1):
                score_text = f'{r["match_score"]}% preference match' if r['match_score'] is not None else 'Price-ranked'
                print(f'\n{idx}. {r["product_name"]} | {r["color"]} | {r["size"]} | BDT {r["price"]:.0f}')
                print('   ', score_text, '| Matches:', r['matched_preferences'] or 'None specified')
                print('   ', r['product_url'])
    except ValueError:
        print('Please enter a numeric budget, e.g. 800.')
    except FileNotFoundError:
        print('Keep both ZAVRA CSV files in the same folder as this script.')
