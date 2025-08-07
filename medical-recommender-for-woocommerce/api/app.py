"""Flask application for medical product recommendations API."""

import logging
import os
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS

from core.models import Product, Recommendation
from core.recommender import MedicalRecommender
from utils.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global recommender instance
recommender: Optional[MedicalRecommender] = None


def create_app(config_path: Optional[str] = None) -> Flask:
    """Create and configure Flask application.
    
    Args:
        config_path: Path to configuration file (optional)
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Enable CORS for all origins (adjust for production)
    CORS(app, origins="*")
    
    # Initialize global recommender
    global recommender
    try:
        # Load configuration
        config = None
        if config_path and os.path.exists(config_path):
            config = Config(config_path)
            logger.info(f"Loaded configuration from {config_path}")
        else:
            # Try to load from default .env
            env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
            if os.path.exists(env_path):
                config = Config(env_path)
                logger.info("Loaded configuration from .env")
        
        # Initialize recommender with optional WooCommerce integration
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.csv')
        recommender = MedicalRecommender(products_file=csv_path, config=config)
        
        # Try to load from cache or WooCommerce if available
        if recommender.woo_client and recommender.cache:
            if recommender.cache.is_cache_valid():
                cached_products = recommender.cache.load_products()
                if cached_products:
                    recommender.products = cached_products
                    recommender._group_products_by_category()
                    logger.info(f"Loaded {len(cached_products)} products from cache")
            else:
                logger.info("Cache expired or invalid, using CSV data")
        
        logger.info(f"Recommender initialized with {len(recommender.products)} products")
        
    except Exception as e:
        logger.error(f"Failed to initialize recommender: {e}")
        # Initialize with basic CSV data as fallback
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.csv')
        recommender = MedicalRecommender(products_file=csv_path)
        logger.warning("Using fallback CSV data only")
    
    # Register routes
    register_routes(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def register_routes(app: Flask) -> None:
    """Register API routes.
    
    Args:
        app: Flask application instance
    """
    
    @app.route('/', methods=['GET'])
    def health_check() -> Dict[str, Any]:
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "message": "Medical Product Recommender API",
            "version": "1.0.0",
            "products_count": len(recommender.products) if recommender else 0,
            "woocommerce_enabled": bool(recommender and recommender.woo_client),
            "cache_enabled": bool(recommender and recommender.cache)
        })
    
    @app.route('/recommend', methods=['GET'])
    def get_recommendations() -> Dict[str, Any]:
        """Get product recommendations based on query.
        
        Query Parameters:
            input (str): Search query (profession, health condition, etc.)
            limit (int, optional): Maximum number of recommendations (default: 10)
            format (str, optional): Response format ('json' or 'simple', default: 'json')
            
        Returns:
            JSON response with recommendations
        """
        if not recommender:
            return jsonify({
                "error": "Recommender not initialized",
                "code": "SERVICE_UNAVAILABLE"
            }), 503
        
        # Get query parameters
        query = request.args.get('input', '').strip()
        limit = request.args.get('limit', '10')
        response_format = request.args.get('format', 'json').lower()
        
        # Validate input
        if not query:
            return jsonify({
                "error": "Missing required parameter 'input'",
                "code": "MISSING_PARAMETER",
                "example": "/recommend?input=cukrzyca"
            }), 400
        
        try:
            limit = int(limit)
            if limit <= 0 or limit > 100:
                limit = 10
        except ValueError:
            limit = 10
        
        try:
            # Generate recommendations
            recommendation = recommender.recommend(query)
            
            # Limit results
            limited_products = recommendation.products[:limit]
            recommendation.products = limited_products
            
            if response_format == 'simple':
                # Simple format for easy frontend consumption
                return jsonify({
                    "query": recommendation.query,
                    "confidence": recommendation.confidence,
                    "count": len(recommendation.products),
                    "products": [
                        {
                            "id": product.id,
                            "name": product.name,
                            "category": product.category,
                            "price": product.price,
                            "description": product.description[:200] + "..." if len(product.description) > 200 else product.description
                        }
                        for product in recommendation.products
                    ]
                })
            else:
                # Full format with all details
                return jsonify({
                    "query": recommendation.query,
                    "confidence": recommendation.confidence,
                    "reasoning": recommendation.reasoning,
                    "count": len(recommendation.products),
                    "products": [product.to_dict() if hasattr(product, 'to_dict') else {
                        "id": product.id,
                        "name": product.name,
                        "category": product.category,
                        "price": product.price,
                        "description": product.description
                    } for product in recommendation.products],
                    "meta": {
                        "total_products_available": len(recommender.products),
                        "categories_available": len(recommender.get_categories()),
                        "woocommerce_enabled": bool(recommender.woo_client),
                        "cache_info": recommender.get_cache_info() if recommender.cache else None
                    }
                })
                
        except Exception as e:
            logger.error(f"Error generating recommendations for '{query}': {e}")
            return jsonify({
                "error": "Failed to generate recommendations",
                "code": "RECOMMENDATION_ERROR",
                "message": str(e)
            }), 500
    
    @app.route('/products', methods=['GET'])
    def get_products() -> Dict[str, Any]:
        """Get list of available products.
        
        Query Parameters:
            category (str, optional): Filter by category
            limit (int, optional): Maximum number of products (default: 50)
            offset (int, optional): Number of products to skip (default: 0)
            
        Returns:
            JSON response with product list
        """
        if not recommender:
            return jsonify({
                "error": "Recommender not initialized",
                "code": "SERVICE_UNAVAILABLE"
            }), 503
        
        # Get query parameters
        category = request.args.get('category', '').strip().lower()
        limit = request.args.get('limit', '50')
        offset = request.args.get('offset', '0')
        
        try:
            limit = int(limit)
            offset = int(offset)
            
            if limit <= 0 or limit > 1000:
                limit = 50
            if offset < 0:
                offset = 0
                
        except ValueError:
            limit = 50
            offset = 0
        
        try:
            products = recommender.products
            
            # Filter by category if specified
            if category:
                products = [p for p in products if p.category.lower() == category]
            
            # Apply pagination
            total_count = len(products)
            paginated_products = products[offset:offset + limit]
            
            return jsonify({
                "products": [
                    {
                        "id": product.id,
                        "name": product.name,
                        "category": product.category,
                        "price": product.price,
                        "description": product.description[:200] + "..." if len(product.description) > 200 else product.description
                    }
                    for product in paginated_products
                ],
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_next": offset + limit < total_count,
                    "has_prev": offset > 0
                },
                "meta": {
                    "categories_available": sorted(recommender.get_categories()),
                    "woocommerce_enabled": bool(recommender.woo_client)
                }
            })
            
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            return jsonify({
                "error": "Failed to fetch products",
                "code": "PRODUCTS_ERROR",
                "message": str(e)
            }), 500
    
    @app.route('/categories', methods=['GET'])
    def get_categories() -> Dict[str, Any]:
        """Get list of available product categories.
        
        Returns:
            JSON response with category list and statistics
        """
        if not recommender:
            return jsonify({
                "error": "Recommender not initialized",
                "code": "SERVICE_UNAVAILABLE"
            }), 503
        
        try:
            categories = {}
            for product in recommender.products:
                category = product.category
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
            
            return jsonify({
                "categories": [
                    {
                        "name": category,
                        "product_count": count
                    }
                    for category, count in sorted(categories.items())
                ],
                "total_categories": len(categories),
                "total_products": len(recommender.products)
            })
            
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return jsonify({
                "error": "Failed to fetch categories",
                "code": "CATEGORIES_ERROR",
                "message": str(e)
            }), 500


def register_error_handlers(app: Flask) -> None:
    """Register error handlers for Flask application.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(404)
    def not_found(error) -> tuple:
        """Handle 404 errors."""
        return jsonify({
            "error": "Endpoint not found",
            "code": "NOT_FOUND",
            "available_endpoints": [
                "GET /",
                "GET /recommend?input=<query>",
                "GET /products",
                "GET /categories"
            ]
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error) -> tuple:
        """Handle 405 errors."""
        return jsonify({
            "error": "Method not allowed",
            "code": "METHOD_NOT_ALLOWED"
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error) -> tuple:
        """Handle 500 errors."""
        logger.error(f"Internal server error: {error}")
        return jsonify({
            "error": "Internal server error",
            "code": "INTERNAL_ERROR"
        }), 500


def main() -> None:
    """Run the Flask development server."""
    app = create_app()
    
    # Development configuration
    app.config['DEBUG'] = True
    app.config['DEVELOPMENT'] = True
    
    logger.info("Starting Medical Product Recommender API server...")
    logger.info("Available endpoints:")
    logger.info("  GET / - Health check")
    logger.info("  GET /recommend?input=<query> - Get recommendations")
    logger.info("  GET /products - List products")
    logger.info("  GET /categories - List categories")
    
    # Run development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )


if __name__ == '__main__':
    main()
