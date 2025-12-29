from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
import json
import logging
from pathlib import Path
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))

app = Flask(__name__, static_folder='.')
CORS(app)

from xray.storage import save_execution
from demo.demo_app import demo_workflow_orchestrator


@app.route('/')
def index():
    return send_from_directory('.', 'dashboard.html')


@app.route('/xray_data/<path:filename>')
def serve_xray_data(filename):
    return send_from_directory('xray_data', filename)


@app.route('/api/demo/run', methods=['POST'])
def run_demo():
    """API endpoint that validates parameters and runs the demo workflow."""
    try:
        params = request.json or {}
        
        # Validate num_candidates
        num_candidates = params.get('num_candidates', 50)
        if not isinstance(num_candidates, int):
            return jsonify({
                "success": False,
                "error": "num_candidates must be an integer"
            }), 400
        if num_candidates < 1 or num_candidates > 1000:
            return jsonify({
                "success": False,
                "error": "num_candidates must be between 1 and 1000"
            }), 400
        
        # Validate min_price_multiplier
        min_price_mult = params.get('min_price_multiplier', 0.5)
        if not isinstance(min_price_mult, (int, float)):
            return jsonify({
                "success": False,
                "error": "min_price_multiplier must be a number"
            }), 400
        if min_price_mult <= 0:
            return jsonify({
                "success": False,
                "error": "min_price_multiplier must be greater than 0"
            }), 400
        
        # Validate max_price_multiplier
        max_price_mult = params.get('max_price_multiplier', 2.0)
        if not isinstance(max_price_mult, (int, float)):
            return jsonify({
                "success": False,
                "error": "max_price_multiplier must be a number"
            }), 400
        if max_price_mult <= min_price_mult:
            return jsonify({
                "success": False,
                "error": "max_price_multiplier must be greater than min_price_multiplier"
            }), 400
        
        # Validate min_rating
        min_rating = params.get('min_rating', 3.8)
        if not isinstance(min_rating, (int, float)):
            return jsonify({
                "success": False,
                "error": "min_rating must be a number"
            }), 400
        if min_rating < 1.0 or min_rating > 5.0:
            return jsonify({
                "success": False,
                "error": "min_rating must be between 1.0 and 5.0"
            }), 400
        
        # Validate min_reviews
        min_reviews = params.get('min_reviews', 100)
        if not isinstance(min_reviews, int):
            return jsonify({
                "success": False,
                "error": "min_reviews must be an integer"
            }), 400
        if min_reviews < 0:
            return jsonify({
                "success": False,
                "error": "min_reviews must be non-negative"
            }), 400
        
        logger.info(f"Running demo with params: num_candidates={num_candidates}, "
                   f"price_mult={min_price_mult}-{max_price_mult}, "
                   f"min_rating={min_rating}, min_reviews={min_reviews}")
        
        # Run the workflow orchestrator
        execution_data = demo_workflow_orchestrator({
            'num_candidates': num_candidates,
            'min_price_multiplier': min_price_mult,
            'max_price_multiplier': max_price_mult,
            'min_rating': min_rating,
            'min_reviews': min_reviews
        })
        
        # Save execution
        filepath = save_execution(execution_data, filename="demo_execution.json")
        
        logger.info(f"Demo completed successfully. Execution ID: {execution_data['id']}")
        
        return jsonify({
            "success": True,
            "execution_id": execution_data['id'],
            "execution_data": execution_data,
            "filepath": filepath
        })
        
    except ValueError as e:
        logger.warning(f"Validation error in run_demo: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        logger.exception(f"Unexpected error in run_demo: {e}")
        return jsonify({
            "success": False,
            "error": "An internal error occurred. Please check the server logs."
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
