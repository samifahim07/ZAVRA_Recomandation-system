"""Build a portable, pickle-serialized recommendation snapshot from Shopify CSV data."""
import csv
import pickle
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
with (HERE / 'ZAVRA_All_Shirts_Variants.csv').open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))

# PKL stores inventory data + ranking configuration, not a fitted ML estimator.
model = {
    'version': 1,
    'generated_at_utc': datetime.now(timezone.utc).isoformat(),
    'source': 'ZAVRA Shopify catalog snapshot, updated 2026-10-09',
    'weights': {'fabric': 45, 'color': 40, 'occasion': 15},
    'variants': rows,
}
with (HERE / 'zavra_recommender.pkl').open('wb') as f:
    pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)
print(f"Saved {len(rows)} variants to zavra_recommender.pkl")
