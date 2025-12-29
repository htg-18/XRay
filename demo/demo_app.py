import sys
sys.path.insert(0, '..')

from .mock_data import get_reference_product, get_mock_search_results
from xray import XRay


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


def demo_workflow_orchestrator(params: dict):
    """
    Orchestrate the full competitor selection workflow with X-Ray tracking.
    
    Args:
        params: Dictionary containing workflow parameters:
            - num_candidates (int): Number of products to fetch
            - min_price_multiplier (float): Min price multiplier vs reference
            - max_price_multiplier (float): Max price multiplier vs reference
            - min_rating (float): Minimum star rating
            - min_reviews (int): Minimum review count
    
    Returns:
        dict: X-Ray execution data with full workflow trace
    """
    num_candidates = params.get('num_candidates', 50)
    min_price_mult = params.get('min_price_multiplier', 0.5)
    max_price_mult = params.get('max_price_multiplier', 2.0)
    min_rating = params.get('min_rating', 3.8)
    min_reviews = params.get('min_reviews', 100)
    
    reference_product = get_reference_product()
    
    with XRay.start("competitor_product_selection", tags={"demo": True, "api": True}) as xray:
        
        # Step 1: Keyword Generation
        with xray.step("keyword_generation", step_type="llm", 
                       reasoning="Extract key search terms from product title") as step:
            step.set_input(
                product_title=reference_product['title'],
                category=reference_product['category']
            )
            
            keyword_result = generate_keywords(reference_product)
            keywords = keyword_result['keywords']
            
            step.set_output(keyword_result)
            step.set_metadata(model="mock-gpt-4", temperature=0.7)
            
            extraction_parts = []
            if 'material' in keyword_result['extraction_logic']:
                extraction_parts.append(f"material ({keyword_result['extraction_logic']['material']})")
            if 'capacity' in keyword_result['extraction_logic']:
                extraction_parts.append(f"capacity ({keyword_result['extraction_logic']['capacity']})")
            if 'feature' in keyword_result['extraction_logic']:
                extraction_parts.append(f"feature ({keyword_result['extraction_logic']['feature']})")
            
            step.set_reasoning(
                f"LLM extracted {len(keywords)} search keywords by identifying key product attributes: "
                f"{', '.join(extraction_parts)}. "
                f"These keywords will be used to query the search API for similar products. "
                f"Strategy: Cast a wide net with variations to maximize relevant results."
            )
        
        # Step 2: Search Products
        with xray.step("search_products", step_type="api",
                       reasoning="Retrieve candidate products from search API") as step:
            step.set_input(keywords=keywords, limit=num_candidates)
            
            candidates = get_mock_search_results(num_candidates)
            
            step.set_output({
                "total_results": 2847,
                "fetched": len(candidates),
                "keywords_used": len(keywords)
            })
            
            step.set_reasoning(
                f"Search API queried using {len(keywords)} keywords: {', '.join(keywords)}. "
                f"Retrieved {len(candidates)} candidate products from 2,847 total matches in catalog. "
                f"Results sorted by relevance score (combination of text match, sales rank, and customer ratings). "
                f"Requested {num_candidates} products, received {len(candidates)}."
            )
        
        # Step 3: Apply Filters
        with xray.step("apply_filters", step_type="filter",
                       reasoning="Filter candidates by price, rating, and review count") as step:
            
            ref_price = reference_product['price']
            calc_min_price = ref_price * min_price_mult
            calc_max_price = ref_price * max_price_mult
            
            step.set_input(
                candidates_count=len(candidates),
                reference_product={
                    "title": reference_product['title'],
                    "price": reference_product['price'],
                    "rating": reference_product['rating'],
                    "reviews": reference_product['reviews']
                },
                filters={
                    "price_range": f"${calc_min_price:.2f} - ${calc_max_price:.2f}",
                    "min_rating": f"{min_rating}★",
                    "min_reviews": str(min_reviews)
                }
            )
            
            qualified = []
            price_failures = 0
            rating_failures = 0
            review_failures = 0
            
            with step.evaluation_stream() as stream:
                for product in candidates:
                    evaluation = _evaluate_product_with_params(
                        product, 
                        reference_product,
                        min_price_mult,
                        max_price_mult,
                        min_rating,
                        min_reviews
                    )
                    stream.write(evaluation)
                    
                    if evaluation["qualified"]:
                        qualified.append(product)
                    else:
                        for check in evaluation['checks']:
                            if not check['passed']:
                                if check['name'] == 'price_range':
                                    price_failures += 1
                                elif check['name'] == 'min_rating':
                                    rating_failures += 1
                                elif check['name'] == 'min_reviews':
                                    review_failures += 1
            
            step.set_output({
                "qualified_count": len(qualified),
                "failed_count": len(candidates) - len(qualified),
                "failure_breakdown": {
                    "price_out_of_range": price_failures,
                    "rating_too_low": rating_failures,
                    "insufficient_reviews": review_failures
                }
            })
            
            pass_rate = (len(qualified) / len(candidates) * 100) if candidates else 0
            step.set_reasoning(
                f"Applied 3-stage filter to {len(candidates)} candidates: "
                f"(1) Price range ${calc_min_price:.2f}-${calc_max_price:.2f} ({min_price_mult}x-{max_price_mult}x reference price of ${ref_price}), "
                f"(2) Minimum rating {min_rating}★ (comparable quality), "
                f"(3) Minimum {min_reviews} reviews (sufficient data confidence). "
                f"Results: {len(qualified)} passed ({pass_rate:.1f}% pass rate), {len(candidates) - len(qualified)} failed. "
                f"Failure breakdown: {price_failures} price violations, {rating_failures} low ratings, {review_failures} insufficient reviews. "
                f"Multiple filters can fail per product."
            )
        
        # Step 4: LLM Relevance Check
        with xray.step("llm_relevance_check", step_type="llm",
                       reasoning="Use LLM to identify and remove false positives") as step:
            step.set_input(
                candidates_count=len(qualified),
                reference_product={
                    "title": reference_product['title'],
                    "category": reference_product['category']
                },
                prompt_strategy="Compare each candidate title and category against reference to identify non-bottle products"
            )
            
            true_competitors = []
            false_positives = []
            
            for product in qualified:
                relevance = evaluate_relevance(product, reference_product)
                
                if relevance['is_competitor']:
                    true_competitors.append(product)
                else:
                    false_positives.append({
                        "title": product['title'],
                        "reason": relevance['reason'],
                        "confidence": relevance['confidence']
                    })
            
            step.set_output({
                "true_competitors": len(true_competitors),
                "false_positives_removed": len(false_positives),
                "false_positive_examples": false_positives[:3],
                "confidence_threshold": 0.85
            })
            step.set_metadata(model="mock-gpt-4", temperature=0.3)
            
            fp_rate = (len(false_positives) / len(qualified) * 100) if qualified else 0
            step.set_reasoning(
                f"LLM evaluated {len(qualified)} filter-qualified products for relevance. "
                f"Identified {len(false_positives)} false positives ({fp_rate:.1f}% of qualified): "
                f"replacement parts, cleaning accessories, carrying cases, and other non-bottle items. "
                f"These passed numeric filters but aren't actual competitor products. "
                f"Confirmed {len(true_competitors)} as true water bottle competitors. "
                f"LLM confidence threshold: 0.85 (using low temperature 0.3 for consistent classification)."
            )
        
        # Step 5: Rank and Select
        if true_competitors:
            with xray.step("rank_and_select", step_type="ranking",
                           reasoning="Rank by weighted scoring: reviews (60%), rating (30%), price proximity (10%)") as step:
                step.set_input(
                    qualified_count=len(true_competitors),
                    ranking_criteria={
                        "primary": "review_count",
                        "primary_weight": "60%",
                        "secondary": "rating",
                        "secondary_weight": "30%",
                        "tertiary": "price_proximity",
                        "tertiary_weight": "10%",
                        "rationale": "Reviews = social proof, Rating = quality, Price proximity = comparable product tier"
                    }
                )
                
                rank_result = rank_and_select(true_competitors, reference_product)
                winner = rank_result['selected_product']
                winner_scores = rank_result['scores']
                runner_up = rank_result['ranked_list'][1] if len(rank_result['ranked_list']) > 1 else None
                
                top_alternatives = []
                for i, ranked_item in enumerate(rank_result['ranked_list'][1:4], start=2):
                    top_alternatives.append({
                        "rank": i,
                        "title": ranked_item['product']['title'],
                        "price": ranked_item['product']['price'],
                        "rating": ranked_item['product']['rating'],
                        "reviews": ranked_item['product']['reviews'],
                        "total_score": ranked_item['scores']['total_score']
                    })
                
                step.set_output({
                    "selected_asin": winner['asin'],
                    "selected_title": winner['title'],
                    "price": winner['price'],
                    "rating": winner['rating'],
                    "reviews": winner['reviews'],
                    "scores": winner_scores,
                    "top_3_alternatives": top_alternatives
                })
                
                score_diff = winner_scores['total_score'] - runner_up['scores']['total_score'] if runner_up else 0
                step.set_reasoning(
                    f"Ranked {len(true_competitors)} candidates using weighted scoring algorithm: "
                    f"60% review count (social proof / popularity), "
                    f"30% rating (quality signal), "
                    f"10% price proximity (similar market positioning). "
                    f"Winner: '{winner['title']}' with total score {winner_scores['total_score']:.3f} "
                    f"(review score: {winner_scores['review_score']:.3f}, "
                    f"rating score: {winner_scores['rating_score']:.3f}, "
                    f"price score: {winner_scores['price_score']:.3f}). "
                    f"Has highest review count: {winner['reviews']:,} reviews (strong market validation). "
                    + (f"Beat 2nd place by {score_diff:.3f} points ({score_diff/winner_scores['total_score']*100:.1f}% margin)." if runner_up else "")
                )
    
    return xray.to_dict()


def _evaluate_product_with_params(product: dict, reference_product: dict,
                                   min_price_mult: float, max_price_mult: float,
                                   min_rating: float, min_reviews: int) -> dict:
    """Helper function to evaluate a product with custom parameters for streaming."""
    ref_price = reference_product['price']
    min_price = ref_price * min_price_mult
    max_price = ref_price * max_price_mult
    
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

