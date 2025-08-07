"""WooCommerce API client for fetching products."""

import json
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import requests

from utils.config import Config

logger = logging.getLogger(__name__)


class WooCommerceClient:
    """Client for interacting with WooCommerce REST API.
    
    Handles authentication, product fetching, and error handling
    for WooCommerce REST API v3.
    """
    
    def __init__(self, config: Config):
        """Initialize WooCommerce client.
        
        Args:
            config: Application configuration object
            
        Raises:
            ValueError: If WooCommerce is not properly configured
        """
        if not config.is_woocommerce_configured():
            raise ValueError("WooCommerce API not properly configured")
        
        self.config = config
        self.base_url = config.get_woocommerce_base_url()
        self.timeout = config.api_timeout
        
        # Setup authentication
        self.auth = (
            config.woocommerce_consumer_key,
            config.woocommerce_consumer_secret
        )
        
        logger.info(f"WooCommerce client initialized for {config.woocommerce_url}")
    
    def get_products(self, limit: Optional[int] = None, 
                    page: int = 1, status: str = "publish") -> List[Dict[str, Any]]:
        """Fetch products from WooCommerce API.
        
        Args:
            limit: Maximum number of products to fetch (uses config default if None)
            page: Page number for pagination
            status: Product status filter (publish, draft, etc.)
            
        Returns:
            List of product dictionaries from WooCommerce API
            
        Raises:
            requests.RequestException: If API request fails
            ValueError: If response is invalid
        """
        if limit is None:
            limit = self.config.max_products
        
        params = {
            "per_page": min(limit, 100),  # WooCommerce max per page is 100
            "page": page,
            "status": status
        }
        
        url = f"{self.base_url}/products"
        if params:
            url += "?" + urlencode(params)
        
        logger.info(f"Fetching products from WooCommerce: {url}")
        
        try:
            response = requests.get(
                url,
                auth=self.auth,
                timeout=self.timeout,
                headers={"Accept": "application/json"}
            )
            
            response.raise_for_status()
            
            products = response.json()
            
            if not isinstance(products, list):
                raise ValueError("Invalid response format: expected list of products")
            
            logger.info(f"Successfully fetched {len(products)} products from WooCommerce")
            return products
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch products from WooCommerce: {e}")
            raise
    
    def get_all_products(self, status: str = "publish") -> List[Dict[str, Any]]:
        """Fetch all products from WooCommerce using pagination.
        
        Args:
            status: Product status filter
            
        Returns:
            List of all product dictionaries
            
        Raises:
            requests.RequestException: If API request fails
        """
        all_products = []
        page = 1
        max_products = self.config.max_products
        
        logger.info(f"Fetching all products (max: {max_products})")
        
        while len(all_products) < max_products:
            try:
                products = self.get_products(
                    limit=min(100, max_products - len(all_products)),
                    page=page,
                    status=status
                )
                
                if not products:
                    # No more products to fetch
                    break
                
                all_products.extend(products)
                page += 1
                
                # If we got less than 100 products, we've reached the end
                if len(products) < 100:
                    break
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch page {page}: {e}")
                break
        
        logger.info(f"Total products fetched: {len(all_products)}")
        return all_products[:max_products]
    
    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single product by ID.
        
        Args:
            product_id: WooCommerce product ID
            
        Returns:
            Product dictionary or None if not found
            
        Raises:
            requests.RequestException: If API request fails
        """
        url = f"{self.base_url}/products/{product_id}"
        
        logger.info(f"Fetching product {product_id} from WooCommerce")
        
        try:
            response = requests.get(
                url,
                auth=self.auth,
                timeout=self.timeout,
                headers={"Accept": "application/json"}
            )
            
            if response.status_code == 404:
                logger.warning(f"Product {product_id} not found")
                return None
            
            response.raise_for_status()
            product = response.json()
            
            logger.info(f"Successfully fetched product {product_id}")
            return product
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch product {product_id}: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test connection to WooCommerce API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to fetch a single product to test connection
            products = self.get_products(limit=1)
            return len(products) >= 0  # Any response means connection works
            
        except Exception as e:
            logger.error(f"WooCommerce connection test failed: {e}")
            return False
    
    def get_total_products_count(self, status: str = "publish") -> Optional[int]:
        """Get total count of products in WooCommerce without fetching all data.
        
        Args:
            status: Product status filter
            
        Returns:
            Total number of products or None if failed
        """
        try:
            # Make a request with per_page=1 to get total count from headers
            params = {
                "per_page": 1,
                "page": 1,
                "status": status
            }
            
            url = f"{self.base_url}/products?" + urlencode(params)
            logger.info(f"Getting total products count from WooCommerce: {url}")
            
            response = requests.get(
                url,
                auth=self.auth,
                timeout=self.timeout,
                headers={"Accept": "application/json"}
            )
            
            response.raise_for_status()
            
            # WooCommerce returns total count in X-WP-Total header
            total_count = response.headers.get('X-WP-Total')
            if total_count:
                total = int(total_count)
                logger.info(f"Total products in WooCommerce: {total}")
                return total
            else:
                logger.warning("X-WP-Total header not found in response")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get total products count: {e}")
            return None

    def get_store_info(self) -> Optional[Dict[str, Any]]:
        """Get basic store information from WooCommerce.
        
        Returns:
            Store information dictionary or None if failed
        """
        try:
            # Try to access the store endpoint
            store_url = self.config.woocommerce_url.rstrip('/') + "/wp-json"
            response = requests.get(store_url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data.get("name", "Unknown"),
                    "description": data.get("description", ""),
                    "url": data.get("url", ""),
                    "version": data.get("version", "Unknown")
                }
            
        except Exception as e:
            logger.error(f"Failed to get store info: {e}")
        
        return None
