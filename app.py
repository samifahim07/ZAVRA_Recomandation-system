
import os
import math

from flask import Flask, jsonify, request
from flask_cors import CORS
from recommender_engine import load_model, recommend

# Initialize Flask
app = Flask(__name__)

# Load Pickle Recommendation Model
model = load_model()

# Shopify CORS Configuration
origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "https://zavrabd.myshopify.com"
    ).split(",")
    if origin.strip()
]

CORS(
    app,
    resources={
        r"/api/*": {"origins": origins}
    }
)


# Homepage
@app.route("/", methods=["GET"])
def home():
    return """
    <html>
    <head>
        <title>ZAVRA Recommendation System</title>
    </head>
    <body style="background:#101820;color:white;
                 font-family:Arial;text-align:center;
                 padding:100px 20px;">

        <h1>ZAVRA AI Recommendation System</h1>
        <h2 style="color:#3ddc97;">Server Running Successfully!</h2>

        <p>Pickle Recommendation Engine Loaded</p>

        <p>
            <a href="/health" style="color:#3ddc97;">
                Check API Health
            </a>
        </p>

    </body>
    </html>
    """


# Health Check
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "ZAVRA Recommendation API is running",
        "total_variants": len(model["variants"]),
        "source": model["source"]
    })


# Recommendation API
@app.route("/api/recommend", methods=["POST"])
def api_recommend():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "JSON request body required"
        }), 400

    try:
        budget = float(data.get("budget", 800))

        if not math.isfinite(budget) or not 0 < budget <= 100000:
            return jsonify({
                "error": "Invalid budget"
            }), 400

        size = str(data.get("size", "M"))

        if size.strip().upper() not in ("M", "L", "XL", "ANY"):
            return jsonify({
                "error": "Invalid size"
            }), 400

        limit = int(data.get("limit", 3))

        if not 1 <= limit <= 10:
            return jsonify({
                "error": "Invalid recommendation limit"
            }), 400

        recommendations = recommend(
            model,
            budget=budget,
            size=size,
            color=str(data.get("color", "Any"))[:80],
            fabric=str(data.get("fabric", "Any"))[:80],
            occasion=str(data.get("occasion", "Any"))[:80],
            limit=limit
        )

        return jsonify({
            "status": "success",
            "count": len(recommendations),
            "recommendations": recommendations,
            "catalog_updated": "2026-10-09",
            "note": "Verify live inventory and pricing before purchase"
        })

    except (ValueError, TypeError):
        return jsonify({
            "error": "Invalid budget or limit"
        }), 400


# Run Application
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
