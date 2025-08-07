"""Caching utilities for the medical recommender system."""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.models import Product

logger = logging.getLogger(__name__)


class ProductCache:
    """Cache for storing product data locally.
    
    Provides functionality to save and load product data from JSON files
    with automatic expiration based on cache duration.
    """
    
    def __init__(self, cache_dir: str = "data", cache_duration: int = 3600):
        """Initialize product cache.
        
        Args:
            cache_dir: Directory to store cache files
            cache_duration: Cache duration in seconds (default: 1 hour)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_duration = cache_duration
        self.products_file = self.cache_dir / "products.json"
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(exist_ok=True)
        
        logger.info(f"Product cache initialized: {self.cache_dir} (duration: {cache_duration}s)")
    
    def save_products(self, products: List[Product]) -> None:
        """Save products to cache.
        
        Args:
            products: List of Product objects to cache
        """
        try:
            # Convert products to dictionaries
            products_data = []
            for product in products:
                products_data.append({
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "price": product.price,
                    "description": product.description
                })
            
            # Save products data
            with open(self.products_file, 'w', encoding='utf-8') as f:
                json.dump(products_data, f, ensure_ascii=False, indent=2)
            
            # Save metadata
            metadata = {
                "timestamp": time.time(),
                "product_count": len(products),
                "cache_duration": self.cache_duration
            }
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Cached {len(products)} products to {self.products_file}")
            
        except Exception as e:
            logger.error(f"Failed to save products to cache: {e}")
            raise
    
    def load_products(self) -> Optional[List[Product]]:
        """Load products from cache if valid.
        
        Returns:
            List of Product objects if cache is valid, None otherwise
        """
        try:
            # Check if cache files exist
            if not self.products_file.exists() or not self.metadata_file.exists():
                logger.debug("Cache files not found")
                return None
            
            # Load metadata
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Check if cache is expired
            cache_age = time.time() - metadata.get("timestamp", 0)
            if cache_age > self.cache_duration:
                logger.info(f"Cache expired (age: {cache_age:.0f}s, max: {self.cache_duration}s)")
                return None
            
            # Load products data
            with open(self.products_file, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
            
            # Convert back to Product objects
            products = []
            for product_data in products_data:
                try:
                    product = Product(
                        id=product_data["id"],
                        name=product_data["name"],
                        category=product_data["category"],
                        price=product_data["price"],
                        description=product_data["description"]
                    )
                    products.append(product)
                except Exception as e:
                    logger.warning(f"Failed to load cached product {product_data.get('id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Loaded {len(products)} products from cache (age: {cache_age:.0f}s)")
            return products
            
        except Exception as e:
            logger.error(f"Failed to load products from cache: {e}")
            return None
    
    def is_cache_valid(self) -> bool:
        """Check if cache is valid and not expired.
        
        Returns:
            True if cache exists and is not expired
        """
        try:
            if not self.metadata_file.exists():
                return False
            
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            cache_age = time.time() - metadata.get("timestamp", 0)
            return cache_age <= self.cache_duration
            
        except Exception as e:
            logger.error(f"Failed to check cache validity: {e}")
            return False
    
    def get_cache_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current cache.
        
        Returns:
            Dictionary with cache information or None if no cache
        """
        try:
            if not self.metadata_file.exists():
                return None
            
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            cache_age = time.time() - metadata.get("timestamp", 0)
            is_expired = cache_age > self.cache_duration
            
            return {
                "timestamp": metadata.get("timestamp"),
                "age_seconds": cache_age,
                "age_human": f"{cache_age / 3600:.1f} hours",
                "product_count": metadata.get("product_count", 0),
                "cache_duration": metadata.get("cache_duration"),
                "is_expired": is_expired,
                "is_valid": not is_expired
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache info: {e}")
            return None
    
    def clear_cache(self) -> None:
        """Clear the cache by removing cache files."""
        try:
            if self.products_file.exists():
                self.products_file.unlink()
                logger.info("Removed products cache file")
            
            if self.metadata_file.exists():
                self.metadata_file.unlink()
                logger.info("Removed cache metadata file")
                
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    def update_cache_duration(self, new_duration: int) -> None:
        """Update cache duration.
        
        Args:
            new_duration: New cache duration in seconds
        """
        self.cache_duration = new_duration
        logger.info(f"Updated cache duration to {new_duration} seconds")
    
    def get_cache_size(self) -> int:
        """Get total size of cache files in bytes.
        
        Returns:
            Total size in bytes
        """
        total_size = 0
        
        if self.products_file.exists():
            total_size += self.products_file.stat().st_size
        
        if self.metadata_file.exists():
            total_size += self.metadata_file.stat().st_size
        
        return total_size
