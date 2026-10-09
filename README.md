# ZAVRA Shopify Recommendation API

This package connects ZAVRA's existing Shopify storefront with a lightweight recommendation service.

## Included
- `zavra_recommender.pkl`: serialized catalog (33 variants) + ranking weights; **not a trained predictive ML model**
- `recommender_engine.py`: stock-aware, rule-based ranking (fabric 45%, color 40%, occasion 15%, normalized over active preferences)
- `app.py`: Flask `/api/recommend` endpoint; `/health` check
- `shopify_widget.liquid`: storefront frontend integration snippet
- `build_model.py`: regenerate `.pkl` after CSV refresh
- two source CSV files and Render deployment configuration

## Local setup
```bash
pip install -r requirements.txt
python app.py
```
Test with `POST http://127.0.0.1:5000/api/recommend` and JSON:
```json
{"budget":800,"size":"M","color":"Black","fabric":"Chinese Micro","occasion":"Office"}
```

## Render deployment
1. Upload all files from this directory to a GitHub repository (keep the `.pkl`, `app.py`, and `recommender_engine.py` together).
2. Create a Render **Web Service**, Python runtime.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Environment variable `ALLOWED_ORIGINS`: your Shopify storefront origin, e.g. `https://zavrabd.myshopify.com`. If using a custom domain, include it too separated by commas, e.g. `https://zavrabd.myshopify.com,https://zavra.example`.
6. Confirm `https://YOUR-SERVICE.onrender.com/health` returns JSON.

## Shopify Theme integration
1. Shopify Admin > Online Store > Themes > **Edit code** (make a backup/duplicate theme first).
2. Create a **Custom liquid** section or snippet using `shopify_widget.liquid` as the source.
3. In the widget JavaScript replace the placeholder `API_BASE` with your deployed Render HTTPS service URL.
4. Place it on a page/section such as “Find My Shirt” and test on the real storefront.
5. Actual steps differ between Shopify themes and permissions. If script tags are stripped from Custom Liquid, use an asset JS file and include it from the theme instead.

## Important limitations
- This is a **snapshot** of inventory from 2026-10-09. To avoid outdated prices or out-of-stock recommendations, regularly re-export the Shopify CSV, rebuild pickle (`python build_model.py`), and redeploy. For production, implement live Shopify inventory/price lookups through an authorized Shopify integration.
- The backend is a public read-only recommendation endpoint. Restricting CORS origin is not authentication, so do not expose customer data or admin API tokens. Add rate limits/monitoring before heavy traffic.
- Only unpickle models created by you from trusted sources; pickle files can execute arbitrary code.
- Similarity/ranking scores are preference matches, not trained AI prediction probabilities.
