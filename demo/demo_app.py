import sys
sys.path.insert(0, '..')

from .mock_data import get_reference_product, get_mock_search_results


def generate_keywords(product: dict) -> dict:
    title = product['title'].lower()
    
    keywords = []
    extraction_logic = {}
    
    if 'stainless steel' in title or 'steel' in title:
        keywords.append('stainless steel water bottle')
        extraction_logic['material'] = 'stainless steel'
    
    if '32oz' in title or '30oz' in title:
        keywords.append('insulated water bottle 32oz')
        extraction_logic['capacity'] = '32oz'

    if 'insulated' in title:
        keywords.append('vacuum insulated bottle')
        extraction_logic['feature'] = 'insulated'
    
    if not keywords:
        keywords = ['water bottle']
        extraction_logic['fallback'] = True
    
    return {
        "keywords": keywords,
        "extraction_logic": extraction_logic,
        "total_generated": len(keywords)
    }


def search_products(keywords: list, limit: int = 50) -> list:
    return get_mock_search_results(limit)


def evaluate_product(product: dict, reference_product: dict) -> dict:
    ref_price = reference_product['price']
    min_price = ref_price * 0.5
    max_price = ref_price * 2.0
    min_rating = 3.8
    min_reviews = 100
    
    price_check = {
        "name": "price_range",
        "passed": min_price <= product['price'] <= max_price,
        "detail": f"${product['price']} vs range ${min_price:.2f}-${max_price:.2f}"
    }
    
    rating_check = {
        "name": "min_rating",
        "passed": product['rating'] >= min_rating,
        "detail": f"{product['rating']}★ vs minimum {min_rating}★"
    }
    
    review_check = {
        "name": "min_reviews",
        "passed": product['reviews'] >= min_reviews,
        "detail": f"{product['reviews']:,} vs minimum {min_reviews:,}"
    }
    
    all_passed = all([
        price_check['passed'],
        rating_check['passed'],
        review_check['passed']
    ])
    
    return {
        "item_id": product['asin'],
        "item_data": {
            "title": product['title'],
            "price": product['price'],
            "rating": product['rating'],
            "reviews": product['reviews']
        },
        "checks": [price_check, rating_check, review_check],
        "qualified": all_passed
    }


def evaluate_relevance(product: dict, reference_product: dict) -> dict:
    is_competitor = product.get('is_competitor', True)
    
    confidence = 0.95 if is_competitor else 0.98
    
    if not is_competitor:
        if 'replacement' in product['title'].lower() or 'lid' in product['title'].lower():
            reason = "Product is a replacement part/accessory, not a complete bottle"
        elif 'cleaning' in product['title'].lower() or 'brush' in product['title'].lower():
            reason = "Product is a cleaning accessory, not a water bottle"
        elif 'carrier' in product['title'].lower() or 'sleeve' in product['title'].lower():
            reason = "Product is a carrying accessory, not the bottle itself"
        elif 'rack' in product['title'].lower() or 'stand' in product['title'].lower():
            reason = "Product is storage equipment, not a water bottle"
        else:
            reason = "Product is an accessory or related item, not a water bottle"
    else:
        reason = "Product is a water bottle, same category as reference"
    
    return {
        "asin": product['asin'],
        "title": product['title'],
        "is_competitor": is_competitor,
        "confidence": confidence,
        "reason": reason
    }


def rank_and_select(candidates: list, reference_product: dict) -> dict: 
    if not candidates:
        return None
    
    def calculate_score(product):
        review_score = min(product['reviews'] / 10000, 1.0)
        
        rating_score = (product['rating'] - 3.8) / (5.0 - 3.8)
        
        ref_price = reference_product['price']
        price_diff = abs(product['price'] - ref_price)
        max_diff = ref_price 
        price_score = max(0, 1 - (price_diff / max_diff))

        total = (review_score * 0.6) + (rating_score * 0.3) + (price_score * 0.1)
        
        return {
            "review_score": round(review_score, 3),
            "rating_score": round(rating_score, 3),
            "price_score": round(price_score, 3),
            "total_score": round(total, 3)
        }
    
    ranked = []
    for product in candidates:
        scores = calculate_score(product)
        ranked.append({
            "product": product,
            "scores": scores
        })
    
    ranked.sort(key=lambda x: x['scores']['total_score'], reverse=True)
    
    winner = ranked[0]
    return {
        "selected_product": winner['product'],
        "scores": winner['scores'],
        "ranked_list": ranked[:5]  
    }


