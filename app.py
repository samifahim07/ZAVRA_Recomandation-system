"""ZAVRA Shopify widget backend. Run with: python app.py"""
import os
import math
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from recommender_engine import load_model, recommend

BUILD_ID = 'STRICT-FILTER-2026-10-10-V2'
app = Flask(__name__)
model = load_model()

@app.after_request
def no_cache(response):
    response.headers['Cache-Control'] = 'no-store, max-age=0'
    response.headers['X-ZAVRA-Build'] = BUILD_ID
    return response

@app.get('/')
def home():
    return render_template('index.html')


# Replace/update list via ALLOWED_ORIGINS environment variable when deploying.
origins = [x.strip() for x in os.getenv('ALLOWED_ORIGINS', 'https://zavrabd.myshopify.com').split(',') if x.strip()]
CORS(app, resources={r'/api/*': {'origins': origins}}, methods=['GET','POST'], allow_headers=['Content-Type'])

@app.get('/health')
def health():
    return jsonify(status='ok', variants=len(model['variants']), source=model['source'], build=BUILD_ID, strict_filter=True)

@app.post('/api/recommend')
def api_recommend():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error='JSON request body required'), 400
    try:
        budget = float(data.get('budget', 800))
        if not math.isfinite(budget) or not 0 < budget <= 100000:
            raise ValueError('Invalid budget')
        size = str(data.get('size', 'M'))
        if size.strip().upper() not in ('M', 'L', 'XL', 'ANY'):
            return jsonify(error='Size must be M, L, XL, or Any'), 400
        limit_input = data.get('limit')
        limit = None if limit_input in (None, '', 'all', 'Any') else int(limit_input)
        if limit is not None and not 1 <= limit <= 100:
            raise ValueError('Invalid limit')
        result = recommend(model, budget=budget, size=size, color=str(data.get('color', 'Any'))[:80],
                           fabric=str(data.get('fabric', 'Any'))[:80], occasion=str(data.get('occasion', 'Any'))[:80], limit=limit)
        return jsonify(status='success', recommendations=result, count=len(result), build=BUILD_ID, strict_filter=True, catalog_updated='2026-10-09',
                       note='Catalog snapshot: verify live inventory and pricing before purchasing')
    except (ValueError, TypeError):
        return jsonify(error='Invalid budget or limit'), 400

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=int(os.environ.get('PORT', 5000)))
