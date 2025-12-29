"""
Mock data for the competitor product selection demo.
"""

# Reference product (the seller's product we want to find competitors for)
REFERENCE_PRODUCT = {
    "asin": "B0XYZ123",
    "title": "ProBrand Stainless Steel Water Bottle 32oz Insulated",
    "category": "Sports & Outdoors > Water Bottles",
    "price": 29.99,
    "rating": 4.2,
    "reviews": 1247
}

# Mock search results (50 candidate products)
MOCK_SEARCH_RESULTS = [
    # Good competitors (should pass filters)
    {
        "asin": "B0COMP01",
        "title": "HydroFlask 32oz Wide Mouth Insulated",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 44.99,
        "rating": 4.5,
        "reviews": 8932,
        "is_competitor": True
    },
    {
        "asin": "B0COMP02",
        "title": "Yeti Rambler 26oz Stainless Steel",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 34.99,
        "rating": 4.4,
        "reviews": 5621,
        "is_competitor": True
    },
    {
        "asin": "B0COMP03",
        "title": "Stanley Adventure Quencher 30oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 35.00,
        "rating": 4.3,
        "reviews": 4102,
        "is_competitor": True
    },
    {
        "asin": "B0COMP04",
        "title": "Contigo Autoseal Water Bottle 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 24.99,
        "rating": 4.1,
        "reviews": 2318,
        "is_competitor": True
    },
    {
        "asin": "B0COMP05",
        "title": "Takeya Actives Insulated Bottle 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 28.50,
        "rating": 4.4,
        "reviews": 1876,
        "is_competitor": True
    },
    {
        "asin": "B0COMP06",
        "title": "Simple Modern Water Bottle 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 19.99,
        "rating": 4.3,
        "reviews": 3421,
        "is_competitor": True
    },
    {
        "asin": "B0COMP07",
        "title": "Thermos Stainless King 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 32.99,
        "rating": 4.2,
        "reviews": 1654,
        "is_competitor": True
    },
    {
        "asin": "B0COMP08",
        "title": "Klean Kanteen Insulated 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 39.99,
        "rating": 4.4,
        "reviews": 892,
        "is_competitor": True
    },
    
    # Too cheap (price filter failures)
    {
        "asin": "B0FAIL01",
        "title": "Generic Water Bottle 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 8.99,
        "rating": 3.2,
        "reviews": 45,
        "is_competitor": True
    },
    {
        "asin": "B0FAIL02",
        "title": "Budget Plastic Bottle 28oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 11.50,
        "rating": 3.5,
        "reviews": 234,
        "is_competitor": True
    },
    {
        "asin": "B0FAIL03",
        "title": "Cheap Steel Bottle 24oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 12.99,
        "rating": 3.8,
        "reviews": 156,
        "is_competitor": True
    },
    
    # Too expensive (price filter failures)
    {
        "asin": "B0FAIL04",
        "title": "Premium Titanium Water Bottle 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 89.00,
        "rating": 4.8,
        "reviews": 234,
        "is_competitor": True
    },
    {
        "asin": "B0FAIL05",
        "title": "Luxury Designer Bottle 30oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 125.00,
        "rating": 4.6,
        "reviews": 87,
        "is_competitor": True
    },
    {
        "asin": "B0FAIL06",
        "title": "Gold Plated Water Flask 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 199.99,
        "rating": 4.2,
        "reviews": 23,
        "is_competitor": True
    },
    
    # Low rating (rating filter failures)
    {
        "asin": "B0FAIL07",
        "title": "Mediocre Bottle 32oz Steel",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 25.99,
        "rating": 3.2,
        "reviews": 432,
        "is_competitor": True
    },
    {
        "asin": "B0FAIL08",
        "title": "Poor Quality Insulated 30oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 22.50,
        "rating": 3.5,
        "reviews": 678,
        "is_competitor": True
    },
    {
        "asin": "B0FAIL09",
        "title": "Leaky Bottle 32oz Stainless",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 28.00,
        "rating": 3.0,
        "reviews": 892,
        "is_competitor": True
    },
    
    # Low review count (review filter failures)
    {
        "asin": "B0FAIL10",
        "title": "New Brand Water Bottle 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 27.99,
        "rating": 4.5,
        "reviews": 45,
        "is_competitor": True
    },
    {
        "asin": "B0FAIL11",
        "title": "Startup Bottle Co 30oz Insulated",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 31.00,
        "rating": 4.3,
        "reviews": 23,
        "is_competitor": True
    },
    {
        "asin": "B0FAIL12",
        "title": "Unknown Brand Steel Flask 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 29.99,
        "rating": 4.4,
        "reviews": 67,
        "is_competitor": True
    },
    
    # False positives (accessories, not actual bottles)
    {
        "asin": "B0FALSE01",
        "title": "Replacement Lid for HydroFlask 32oz",
        "category": "Sports & Outdoors > Water Bottle Accessories",
        "price": 12.99,
        "rating": 4.6,
        "reviews": 3421,
        "is_competitor": False
    },
    {
        "asin": "B0FALSE02",
        "title": "Water Bottle Cleaning Brush Set",
        "category": "Home & Kitchen > Cleaning Supplies",
        "price": 9.99,
        "rating": 4.7,
        "reviews": 8234,
        "is_competitor": False
    },
    {
        "asin": "B0FALSE03",
        "title": "Bottle Carrier Bag with Shoulder Strap",
        "category": "Sports & Outdoors > Water Bottle Accessories",
        "price": 15.99,
        "rating": 4.3,
        "reviews": 1234,
        "is_competitor": False
    },
    {
        "asin": "B0FALSE04",
        "title": "Stainless Steel Straw Set for Bottles",
        "category": "Home & Kitchen > Drinkware",
        "price": 8.50,
        "rating": 4.5,
        "reviews": 2341,
        "is_competitor": False
    },
    {
        "asin": "B0FALSE05",
        "title": "Bottle Insulation Sleeve 32oz",
        "category": "Sports & Outdoors > Water Bottle Accessories",
        "price": 14.99,
        "rating": 4.1,
        "reviews": 567,
        "is_competitor": False
    },
    
    # Multiple filter failures (combinations)
    {
        "asin": "B0MULTI01",
        "title": "Cheap Leaky Bottle 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 9.99,
        "rating": 2.8,
        "reviews": 34,
        "is_competitor": True
    },
    {
        "asin": "B0MULTI02",
        "title": "Expensive Unrated Flask 30oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 149.99,
        "rating": 3.5,
        "reviews": 12,
        "is_competitor": True
    },
    {
        "asin": "B0MULTI03",
        "title": "Low Quality Unknown Brand 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 10.50,
        "rating": 3.1,
        "reviews": 23,
        "is_competitor": True
    },
    
    # Edge cases (exactly at boundaries)
    {
        "asin": "B0EDGE01",
        "title": "Edge Case Bottle - Min Price",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 15.00,  # Exactly at minimum (0.5x reference)
        "rating": 3.8,  # Exactly at minimum rating
        "reviews": 100,  # Exactly at minimum reviews
        "is_competitor": True
    },
    {
        "asin": "B0EDGE02",
        "title": "Edge Case Bottle - Max Price",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 59.98,  # Just under maximum (2x reference)
        "rating": 4.0,
        "reviews": 543,
        "is_competitor": True
    },
    {
        "asin": "B0EDGE03",
        "title": "Edge Case - Just Below Min Price",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 14.99,  # Just below minimum
        "rating": 4.5,
        "reviews": 1000,
        "is_competitor": True
    },
    
    # More good competitors to increase qualified pool
    {
        "asin": "B0GOOD01",
        "title": "CamelBak Chute Mag 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 22.00,
        "rating": 4.3,
        "reviews": 2109,
        "is_competitor": True
    },
    {
        "asin": "B0GOOD02",
        "title": "Nalgene Tritan 32oz Wide Mouth",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 18.99,
        "rating": 4.6,
        "reviews": 4532,
        "is_competitor": True
    },
    {
        "asin": "B0GOOD03",
        "title": "S'well Insulated Bottle 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 41.00,
        "rating": 4.5,
        "reviews": 1987,
        "is_competitor": True
    },
    {
        "asin": "B0GOOD04",
        "title": "Iron Flask Sports Water Bottle 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 26.95,
        "rating": 4.4,
        "reviews": 3245,
        "is_competitor": True
    },
    {
        "asin": "B0GOOD05",
        "title": "Polar Bottle Insulated 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 21.99,
        "rating": 4.2,
        "reviews": 1432,
        "is_competitor": True
    },
    {
        "asin": "B0GOOD06",
        "title": "Fifty/Fifty Vacuum Insulated 34oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 29.95,
        "rating": 4.3,
        "reviews": 876,
        "is_competitor": True
    },
    {
        "asin": "B0GOOD07",
        "title": "Mira Alpine Water Bottle 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 24.50,
        "rating": 4.4,
        "reviews": 1654,
        "is_competitor": True
    },
    {
        "asin": "B0GOOD08",
        "title": "RTIC Outdoors Water Bottle 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 19.99,
        "rating": 4.5,
        "reviews": 2876,
        "is_competitor": True
    },
    {
        "asin": "B0GOOD09",
        "title": "Healthy Human Insulated Bottle 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 27.95,
        "rating": 4.3,
        "reviews": 1234,
        "is_competitor": True
    },
    {
        "asin": "B0GOOD10",
        "title": "Bindle Bottle Stainless 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 23.99,
        "rating": 4.1,
        "reviews": 543,
        "is_competitor": True
    },
    {
        "asin": "B0FAIL13",
        "title": "Ultra Budget Bottle 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 7.99,
        "rating": 3.1,
        "reviews": 89,
        "is_competitor": True
    },
    {
        "asin": "B0FAIL14",
        "title": "Overpriced Designer Flask 30oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 179.99,
        "rating": 4.3,
        "reviews": 45,
        "is_competitor": True
    },
    {
        "asin": "B0FAIL15",
        "title": "Poor Reviews Bottle 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 25.00,
        "rating": 2.9,
        "reviews": 543,
        "is_competitor": True
    },
    {
        "asin": "B0FAIL16",
        "title": "New Launch Bottle 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 28.99,
        "rating": 4.7,
        "reviews": 15,
        "is_competitor": True
    },
    {
        "asin": "B0FAIL17",
        "title": "Cheap Plastic Jug 32oz",
        "category": "Sports & Outdoors > Water Bottles",
        "price": 9.50,
        "rating": 3.4,
        "reviews": 234,
        "is_competitor": True
    },
    {
        "asin": "B0FALSE06",
        "title": "Water Bottle Spout Replacement Kit",
        "category": "Sports & Outdoors > Water Bottle Accessories",
        "price": 11.99,
        "rating": 4.4,
        "reviews": 876,
        "is_competitor": False
    },
    {
        "asin": "B0FALSE07",
        "title": "Bottle Drying Rack Stand",
        "category": "Home & Kitchen > Kitchen Storage",
        "price": 18.50,
        "rating": 4.2,
        "reviews": 654,
        "is_competitor": False
    },
    {
        "asin": "B0FALSE08",
        "title": "Silicone Bottle Boot Protective Sleeve",
        "category": "Sports & Outdoors > Water Bottle Accessories",
        "price": 9.99,
        "rating": 4.0,
        "reviews": 432,
        "is_competitor": False
    },
    {
        "asin": "B0FALSE09",
        "title": "Ice Cube Tray for Water Bottles",
        "category": "Home & Kitchen > Ice Tools",
        "price": 12.99,
        "rating": 4.3,
        "reviews": 1234,
        "is_competitor": False
    },
]


def get_reference_product():
    return REFERENCE_PRODUCT


def get_mock_search_results(limit: int = 50):
    return MOCK_SEARCH_RESULTS[:limit]

