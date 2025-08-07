"""Tests for Flask API endpoints."""

import json
import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from api.app import create_app
from core.models import Product, Recommendation


class TestFlaskAPI:
    """Test cases for Flask API endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create test Flask application."""
        # Create a temporary CSV file for testing
        test_products = [
            "id,name,category,price,description",
            "1,Test Glukometr,diabetologia,99.99,Testowy glukometr do pomiaru cukru",
            "2,Test Rękawiczki,higiena,19.99,Testowe rękawiczki nitrylowe",
            "3,Test Opatrunek,opatrunki,5.99,Testowy opatrunek sterylny"
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('\n'.join(test_products))
            csv_path = f.name
        
        try:
            # Mock the CSV path in app creation
            with patch('api.app.os.path.join') as mock_join:
                mock_join.return_value = csv_path
                app = create_app()
                app.config['TESTING'] = True
                yield app
        finally:
            # Clean up
            if os.path.exists(csv_path):
                os.unlink(csv_path)
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'message' in data
        assert 'version' in data
        assert 'products_count' in data
    
    def test_recommend_endpoint_success(self, client):
        """Test successful recommendation request."""
        response = client.get('/recommend?input=cukrzyca')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'query' in data
        assert 'confidence' in data
        assert 'products' in data
        assert 'count' in data
        assert data['query'] == 'cukrzyca'
        assert isinstance(data['products'], list)
    
    def test_recommend_endpoint_missing_input(self, client):
        """Test recommendation request with missing input."""
        response = client.get('/recommend')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['code'] == 'MISSING_PARAMETER'
    
    def test_recommend_endpoint_with_limit(self, client):
        """Test recommendation request with limit parameter."""
        response = client.get('/recommend?input=higiena&limit=2')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['products']) <= 2
    
    def test_recommend_endpoint_simple_format(self, client):
        """Test recommendation request with simple format."""
        response = client.get('/recommend?input=higiena&format=simple')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'query' in data
        assert 'confidence' in data
        assert 'products' in data
        # Simple format should not have 'reasoning' or 'meta'
        assert 'reasoning' not in data
        assert 'meta' not in data
    
    def test_products_endpoint_success(self, client):
        """Test successful products list request."""
        response = client.get('/products')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'products' in data
        assert 'pagination' in data
        assert 'meta' in data
        assert isinstance(data['products'], list)
    
    def test_products_endpoint_with_category_filter(self, client):
        """Test products list with category filter."""
        response = client.get('/products?category=higiena')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Check if filtering worked (if there are higiena products)
        for product in data['products']:
            assert product['category'] == 'higiena'
    
    def test_products_endpoint_with_pagination(self, client):
        """Test products list with pagination."""
        response = client.get('/products?limit=1&offset=0')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['products']) <= 1
        assert data['pagination']['limit'] == 1
        assert data['pagination']['offset'] == 0
    
    def test_categories_endpoint_success(self, client):
        """Test successful categories list request."""
        response = client.get('/categories')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'categories' in data
        assert 'total_categories' in data
        assert 'total_products' in data
        assert isinstance(data['categories'], list)
        
        # Check category structure
        if data['categories']:
            category = data['categories'][0]
            assert 'name' in category
            assert 'product_count' in category
    
    def test_404_error_handler(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['code'] == 'NOT_FOUND'
        assert 'available_endpoints' in data
    
    def test_405_error_handler(self, client):
        """Test 405 error handling."""
        response = client.post('/')  # POST to GET-only endpoint
        assert response.status_code == 405
        
        data = json.loads(response.data)
        assert data['code'] == 'METHOD_NOT_ALLOWED'
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.get('/')
        assert 'Access-Control-Allow-Origin' in response.headers
    
    @patch('api.app.recommender', None)
    def test_endpoints_with_no_recommender(self, client):
        """Test endpoints when recommender is not initialized."""
        # This test ensures graceful handling when recommender fails to initialize
        
        # Test recommend endpoint
        response = client.get('/recommend?input=test')
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data['code'] == 'SERVICE_UNAVAILABLE'
        
        # Test products endpoint
        response = client.get('/products')
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data['code'] == 'SERVICE_UNAVAILABLE'
        
        # Test categories endpoint
        response = client.get('/categories')
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data['code'] == 'SERVICE_UNAVAILABLE'


class TestAPIIntegration:
    """Integration tests for API with real components."""
    
    def test_recommendation_flow(self):
        """Test full recommendation flow."""
        # Create app with minimal setup
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # Test health check
            response = client.get('/')
            assert response.status_code == 200
            
            # Test recommendation
            response = client.get('/recommend?input=ratownik medyczny')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['query'] == 'ratownik medyczny'
            assert isinstance(data['confidence'], (int, float))
            assert isinstance(data['products'], list)
    
    def test_api_error_handling(self):
        """Test API error handling with edge cases."""
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # Test with empty input
            response = client.get('/recommend?input=')
            assert response.status_code == 400
            
            # Test with invalid limit
            response = client.get('/recommend?input=test&limit=invalid')
            assert response.status_code == 200  # Should default to 10
            
            # Test with very large limit
            response = client.get('/recommend?input=test&limit=9999')
            assert response.status_code == 200  # Should cap at reasonable limit


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
