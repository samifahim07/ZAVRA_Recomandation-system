# ZAVRA | Smart Fashion Recommendation System

A personalized fashion recommendation system designed to enhance the online shopping experience by helping customers discover shirts that match their preferences, budget, and size availability.

Built using **Python, Flask, and a Pickle-based recommendation engine**, the system processes customer preferences and identifies relevant products from ZAVRA's Shopify catalog.

## Official Website

**ZAVRA – Premium Fashion Store**

Explore the official ZAVRA Shopify store to discover its latest shirt collections, available colors, fabrics, and pricing.

**Website:** https://zavrabd.myshopify.com/

**Note:** The recommendation system is currently a locally tested project. Integration with the official ZAVRA Shopify website is planned.


## Project Overview

Online fashion shopping often requires customers to browse multiple products before finding something suitable. ZAVRA Smart Fashion Recommendation System simplifies this process through an intelligent, preference-based product discovery experience.

Customers can specify their budget, preferred fabric, shirt size, color, and occasion. The recommendation engine then filters the available catalog and returns matching products with images, prices, availability details, and direct Shopify product links.

The project is designed for integration directly into the existing ZAVRA Shopify storefront.

## Key Features

- **Personalized Product Discovery:** Recommends shirts based on customer-selected preferences.
- **Budget-Based Filtering:** Displays products within the customer's specified spending limit.
- **Fabric Matching:** Supports Bamboo, Cross, and Chinese Micro fabrics.
- **Color-Based Search:** Matches selected colors without introducing unrelated alternatives.
- **Size Availability Checking:** Excludes variants marked as unavailable.
- **Occasion-Based Filtering:** Helps customers find shirts suitable for office, formal events, business meetings, and everyday wear.
- **Exact-Match Recommendations:** Applies strict filtering to selected product attributes.
- **Product Information Display:** Includes product images, prices, available sizes, and Shopify product links.
- **Responsive User Interface:** Provides a premium shopping experience across desktop and mobile devices.
- **REST API Integration:** Enables communication between the recommendation engine and web interfaces.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | Flask |
| Recommendation Engine | Attribute-Based Filtering and Rule-Based Ranking |
| Model Serialization | Pickle |
| Data Processing | Python, CSV |
| Frontend | HTML, CSS, JavaScript |
| Data Source | Shopify Product Catalog |
| API Communication | REST API, JSON |
| Deployment | Render (Planned) |
| E-Commerce Integration | Shopify (Planned) |

## Recommendation Methodology

The system currently uses a deterministic, attribute-based recommendation approach.

Unlike collaborative filtering, this method does not require historical customer ratings or purchasing behavior.

### 1. Customer Preference Collection

The system collects five primary inputs:

| Input | Description |
|---|---|
| Budget | Maximum preferred spending amount in BDT |
| Size | M, L, XL, or Any |
| Fabric | Bamboo, Cross, Chinese Micro, or Any |
| Color | Preferred shirt color or Any |
| Occasion | Office, Formal, Business Meeting, Everyday, or Any |

### 2. Product Filtering

Products are evaluated against the customer's selected criteria.

The filtering process checks:

- Product price against the selected budget.
- Availability of the requested size.
- Exact fabric compatibility.
- Exact color compatibility.
- Occasion compatibility.

Selecting **Any** removes the restriction for that specific attribute.

### 3. Recommendation Generation

After filtering, eligible products are organized and returned as recommendations.

The system prevents duplicate product entries when multiple size variants correspond to the same product.

If no products satisfy the requested conditions, the interface displays an appropriate no-match message instead of recommending unrelated products.

### 4. Product Presentation

Each recommended product includes:

- Product name
- Fabric and color
- Selected size
- Selling price
- Original price, when available
- Product image
- Availability status
- Shopify product URL

## Dataset Information

The initial dataset was collected from the public ZAVRA Shopify product catalog.

| Dataset Property | Value |
|---|---|
| Total Products | 11 |
| Total Product Variants | 33 |
| Fabric Categories | 3 |
| Product Categories | Formal Shirts |
| Data Format | CSV |
| Initial Catalog Snapshot | October 9, 2026 |

The repository contains two primary datasets:

**ZAVRA_All_Shirts_Products.csv**

Contains product-level information, including product names, fabric types, colors, prices, descriptions, and product URLs.

**ZAVRA_All_Shirts_Variants.csv**

Contains variant-level information, including size, color, price, variant identifiers, and availability status.

**Note:** The current dataset represents a saved catalog snapshot. Product availability and pricing may change over time.

## Project Structure

```text
ZAVRA-Recommendation-System/
│
├── app.py
├── recommender_engine.py
├── build_model.py
├── zavra_recommender.pkl
├── requirements.txt
├── Procfile
├── README.md
│
├── ZAVRA_All_Shirts_Products.csv
├── ZAVRA_All_Shirts_Variants.csv
│
└── templates/
    └── index.html
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

### 5. Open in Browser

```text
http://127.0.0.1:5000/
```

The application will display the ZAVRA recommendation interface.

## API Documentation

The project includes REST API endpoints for accessing recommendation services.

### Health Check

**Endpoint**

```http
GET /health
```

Used to verify that the Flask API and recommendation catalog are accessible.

### Generate Recommendations

**Endpoint**

```http
POST /api/recommend
```

**Example Request**

```json
{
  "budget": 800,
  "size": "M",
  "fabric": "Chinese Micro",
  "color": "Black",
  "occasion": "Office"
}
```

**Example Response**

```json
{
  "status": "success",
  "count": 1,
  "recommendations": [
    {
      "name": "Chinese Micro Fabric Shirt",
      "fabric": "Chinese Micro",
      "color": "Black",
      "size": "M",
      "price_bdt": 600,
      "available": true,
      "match_score": 100.0
    }
  ]
}
```

The response above is simplified for documentation purposes. The actual API returns additional information, including product and variant identifiers, image URLs, and product links.

The match score represents rule-based preference compatibility, not predictive model accuracy.

## Shopify Integration

The system is intended to operate as an embedded product recommendation feature within the existing ZAVRA Shopify storefront.

### Proposed Integration Workflow

1. Deploy the Flask recommendation API to a publicly accessible HTTPS hosting environment.
2. Develop a Shopify-compatible recommendation widget.
3. Add the widget to the existing Shopify homepage.
4. Collect customer preferences directly through the Shopify interface.
5. Send preference data to the Flask API.
6. Display matching products within the existing storefront.
7. Redirect customers to the corresponding Shopify product pages when they select a product.

The integration is designed to retain Shopify's existing shopping cart, checkout process, and product management functionality.

**Current Status:** Local recommendation functionality has been tested. Live Shopify storefront integration remains a planned development stage.

## Future Improvements

- Real-time Shopify product and inventory synchronization.
- Automatic catalog updates for newly added products.
- Customer interaction and preference tracking.
- Personalized recommendations using browsing and purchase history.
- Hybrid content-based and collaborative recommendation algorithms.
- Advanced product similarity analysis.
- Search and filtering performance improvements.
- Recommendation quality monitoring.
- Analytics dashboard for product discovery and customer engagement.

## Current Limitations

- The initial catalog contains a limited number of products.
- Recommendations are generated using product attributes rather than learned customer behavior.
- Inventory and pricing are based on the stored Shopify catalog snapshot.
- The system does not currently perform real-time Shopify inventory synchronization.
- Live storefront integration has not yet been completed.

## Project Objective

To develop a practical and scalable fashion product discovery solution that improves the shopping experience through accurate, transparent, and preference-driven recommendations.

The long-term goal is to evolve the system into a personalized fashion recommendation platform using real customer interaction data and machine learning.

## Developer

**Fahim Abrar Chowdhury**

Machine Learning and Artificial Intelligence Enthusiast

## Project Brand

**ZAVRA**

Smart Fashion Discovery | Personalized Recommendations | Better Shopping Experiences

---

*Developed as an independent recommendation system project for potential integration with the ZAVRA Shopify storefront.*
