"""Test module for WooCommerce integration."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any

import pytest

from utils.config import Config
from utils.cache import ProductCache
from woo.client import WooCommerceClient
from woo.mapper import WooCommerceMapper
from core.models import Product


class TestConfig:
    """Test cases for configuration management."""

    def test_config_creation_without_env_file(self):
        """Test creating config without .env file."""
        config = Config()
        
        # Should have default values
        assert config.cache_duration == 3600
        assert config.max_products == 100
        assert config.api_timeout == 30
        assert config.log_level == "INFO"

    def test_config_woocommerce_not_configured(self):
        """Test WooCommerce configuration check."""
        config = Config()
        
        assert not config.is_woocommerce_configured()
        assert config.woocommerce_url == ""
        assert config.woocommerce_consumer_key == ""
        assert config.woocommerce_consumer_secret == ""

    def test_config_validation_empty(self):
        """Test config validation with empty values."""
        config = Config()
        
        with pytest.raises(ValueError, match="WOOCOMMERCE_URL is required"):
            config.validate()

    def test_config_get_woocommerce_base_url(self):
        """Test getting WooCommerce base URL."""
        config = Config()
        config.woocommerce_url = "https://example.com"
        
        base_url = config.get_woocommerce_base_url()
        assert base_url == "https://example.com/wp-json/wc/v3"

    def test_config_get_woocommerce_base_url_with_slash(self):
        """Test getting WooCommerce base URL with trailing slash."""
        config = Config()
        config.woocommerce_url = "https://example.com/"
        
        base_url = config.get_woocommerce_base_url()
        assert base_url == "https://example.com/wp-json/wc/v3"


class TestProductCache:
    """Test cases for product caching."""

    def create_temp_cache_dir(self):
        """Create temporary cache directory."""
        temp_dir = tempfile.mkdtemp()
        return temp_dir

    def create_sample_products(self):
        """Create sample products for testing."""
        return [
            Product(1, "Product 1", "category1", 10.0, "Description 1"),
            Product(2, "Product 2", "category2", 20.0, "Description 2"),
        ]

    def test_cache_initialization(self):
        """Test cache initialization."""
        cache_dir = self.create_temp_cache_dir()
        
        try:
            cache = ProductCache(cache_dir=cache_dir, cache_duration=1800)
            
            assert cache.cache_dir == Path(cache_dir)
            assert cache.cache_duration == 1800
            assert cache.products_file == Path(cache_dir) / "products.json"
            assert cache.metadata_file == Path(cache_dir) / "cache_metadata.json"
        finally:
            import shutil
            shutil.rmtree(cache_dir)

    def test_save_and_load_products(self):
        """Test saving and loading products."""
        cache_dir = self.create_temp_cache_dir()
        
        try:
            cache = ProductCache(cache_dir=cache_dir, cache_duration=3600)
            products = self.create_sample_products()
            
            # Save products
            cache.save_products(products)
            
            # Load products
            loaded_products = cache.load_products()
            
            assert loaded_products is not None
            assert len(loaded_products) == 2
            assert loaded_products[0].name == "Product 1"
            assert loaded_products[1].name == "Product 2"
            
        finally:
            import shutil
            shutil.rmtree(cache_dir)

    def test_cache_expiration(self):
        """Test cache expiration."""
        cache_dir = self.create_temp_cache_dir()
        
        try:
            # Create cache with very short duration
            cache = ProductCache(cache_dir=cache_dir, cache_duration=1)
            products = self.create_sample_products()
            
            # Save products
            cache.save_products(products)
            
            # Should be valid immediately
            assert cache.is_cache_valid()
            
            # Wait for expiration
            import time
            time.sleep(2)
            
            # Should be expired now
            assert not cache.is_cache_valid()
            
            # Loading should return None
            loaded_products = cache.load_products()
            assert loaded_products is None
            
        finally:
            import shutil
            shutil.rmtree(cache_dir)

    def test_get_cache_info(self):
        """Test getting cache information."""
        cache_dir = self.create_temp_cache_dir()
        
        try:
            cache = ProductCache(cache_dir=cache_dir, cache_duration=3600)
            products = self.create_sample_products()
            
            # Initially no cache
            info = cache.get_cache_info()
            assert info is None
            
            # Save products
            cache.save_products(products)
            
            # Get cache info
            info = cache.get_cache_info()
            assert info is not None
            assert info["product_count"] == 2
            assert info["is_valid"] is True
            assert info["cache_duration"] == 3600
            
        finally:
            import shutil
            shutil.rmtree(cache_dir)


class TestWooCommerceMapper:
    """Test cases for WooCommerce data mapping."""

    def create_sample_woo_product(self) -> Dict[str, Any]:
        """Create sample WooCommerce product data."""
        return {
            "id": 123,
            "name": "Test Stethoscope",
            "price": "150.00",
            "regular_price": "180.00",
            "description": "Professional medical stethoscope",
            "short_description": "High-quality stethoscope",
            "categories": [
                {"id": 1, "name": "Stetoskopy", "slug": "stetoskopy"}
            ]
        }

    def test_map_woo_product_to_product(self):
        """Test mapping WooCommerce product to internal Product."""
        woo_product = self.create_sample_woo_product()
        
        product = WooCommerceMapper.map_woo_product_to_product(woo_product)
        
        assert product.id == 123
        assert product.name == "Test Stethoscope"
        assert product.price == 150.0
        assert product.category == "sprzet_diagnostyczny"  # Mapped from "Stetoskopy"
        assert product.description == "Professional medical stethoscope"

    def test_map_woo_product_invalid_data(self):
        """Test mapping with invalid WooCommerce data."""
        invalid_product = {
            "id": 0,  # Invalid ID
            "name": "",  # Empty name
            "price": "invalid"  # Invalid price
        }
        
        with pytest.raises(ValueError):
            WooCommerceMapper.map_woo_product_to_product(invalid_product)

    def test_map_woo_products_to_products(self):
        """Test mapping multiple WooCommerce products."""
        woo_products = [
            self.create_sample_woo_product(),
            {
                "id": 456,
                "name": "Medical Gloves",
                "price": "25.00",
                "description": "Disposable medical gloves",
                "categories": [
                    {"id": 2, "name": "Rękawice", "slug": "rekawice"}
                ]
            }
        ]
        
        products = WooCommerceMapper.map_woo_products_to_products(woo_products)
        
        assert len(products) == 2
        assert products[0].category == "sprzet_diagnostyczny"  # Stethoscope
        assert products[1].category == "higiena"  # Gloves

    def test_category_mapping(self):
        """Test category mapping functionality."""
        # Test direct mapping
        woo_product = {
            "id": 1,
            "name": "Test Product",
            "price": "100.00",
            "description": "Test description",
            "categories": [
                {"id": 1, "name": "Diabetologia", "slug": "diabetologia"}
            ]
        }
        
        product = WooCommerceMapper.map_woo_product_to_product(woo_product)
        assert product.category == "diabetologia"

        # Test fallback to default category
        woo_product_no_category = {
            "id": 2,
            "name": "Unknown Product",
            "price": "50.00",
            "description": "Unknown category product",
            "categories": []
        }
        
        product = WooCommerceMapper.map_woo_product_to_product(woo_product_no_category)
        assert product.category == "sprzet_diagnostyczny"  # Default category

    def test_price_extraction(self):
        """Test price extraction from different fields."""
        # Test regular price
        woo_product = {
            "id": 1,
            "name": "Test Product",
            "regular_price": "200.00",
            "description": "Test description",
            "categories": []
        }
        
        product = WooCommerceMapper.map_woo_product_to_product(woo_product)
        assert product.price == 200.0

        # Test sale price
        woo_product = {
            "id": 2,
            "name": "Test Product",
            "sale_price": "150.00",
            "description": "Test description",
            "categories": []
        }
        
        product = WooCommerceMapper.map_woo_product_to_product(woo_product)
        assert product.price == 150.0

    def test_get_available_categories(self):
        """Test getting available categories."""
        categories = WooCommerceMapper.get_available_categories()
        
        assert "sprzet_diagnostyczny" in categories
        assert "higiena" in categories
        assert "diabetologia" in categories
        assert "torby" in categories


class TestWooCommerceClient:
    """Test cases for WooCommerce API client."""

    def create_mock_config(self):
        """Create mock configuration for testing."""
        config = Mock(spec=Config)
        config.woocommerce_url = "https://example.com"
        config.woocommerce_consumer_key = "test_key"
        config.woocommerce_consumer_secret = "test_secret"
        config.api_timeout = 30
        config.max_products = 100
        config.is_woocommerce_configured.return_value = True
        config.get_woocommerce_base_url.return_value = "https://example.com/wp-json/wc/v3"
        return config

    def test_client_initialization(self):
        """Test WooCommerce client initialization."""
        config = self.create_mock_config()
        
        client = WooCommerceClient(config)
        
        assert client.config == config
        assert client.base_url == "https://example.com/wp-json/wc/v3"
        assert client.timeout == 30
        assert client.auth == ("test_key", "test_secret")

    def test_client_initialization_not_configured(self):
        """Test client initialization with invalid config."""
        config = Mock(spec=Config)
        config.is_woocommerce_configured.return_value = False
        
        with pytest.raises(ValueError, match="WooCommerce API not properly configured"):
            WooCommerceClient(config)

    @patch('requests.get')
    def test_get_products_success(self, mock_get):
        """Test successful product fetching."""
        config = self.create_mock_config()
        client = WooCommerceClient(config)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": 1, "name": "Product 1", "price": "100.00"},
            {"id": 2, "name": "Product 2", "price": "200.00"}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        products = client.get_products(limit=2)
        
        assert len(products) == 2
        assert products[0]["id"] == 1
        assert products[1]["id"] == 2
        
        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "https://example.com/wp-json/wc/v3/products" in call_args[0][0]
        assert call_args[1]["auth"] == ("test_key", "test_secret")

    @patch('requests.get')
    def test_get_products_api_error(self, mock_get):
        """Test handling of API errors."""
        config = self.create_mock_config()
        client = WooCommerceClient(config)
        
        # Mock API error
        mock_get.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            client.get_products()

    def test_test_connection(self):
        """Test connection testing."""
        config = self.create_mock_config()
        client = WooCommerceClient(config)
        
        # Mock successful connection test
        with patch.object(client, 'get_products') as mock_get_products:
            mock_get_products.return_value = [{"id": 1}]
            
            result = client.test_connection()
            assert result is True

        # Mock failed connection test
        with patch.object(client, 'get_products') as mock_get_products:
            mock_get_products.side_effect = Exception("Connection failed")
            
            result = client.test_connection()
            assert result is False
