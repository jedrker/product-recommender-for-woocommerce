"""Test module for core.recommender."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from core.models import Product
from core.recommender import MedicalRecommender


class TestMedicalRecommender:
    """Test cases for MedicalRecommender class."""

    def create_test_csv(self, products_data):
        """Create a temporary CSV file with test products."""
        df = pd.DataFrame(products_data)
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df.to_csv(temp_file.name, index=False)
        temp_file.close()
        return temp_file.name

    def test_load_products_valid_csv(self):
        """Test loading products from valid CSV file."""
        products_data = [
            {"id": 1, "name": "Product 1", "category": "cat1", "price": 10.0, "description": "Desc 1"},
            {"id": 2, "name": "Product 2", "category": "cat2", "price": 20.0, "description": "Desc 2"},
        ]
        
        csv_file = self.create_test_csv(products_data)
        
        try:
            recommender = MedicalRecommender(csv_file)
            
            assert recommender.get_products_count() == 2
            assert len(recommender.get_categories()) == 2
            assert "cat1" in recommender.get_categories()
            assert "cat2" in recommender.get_categories()
        finally:
            Path(csv_file).unlink()

    def test_load_products_file_not_found(self):
        """Test error handling when CSV file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            MedicalRecommender("nonexistent_file.csv")

    def test_load_products_invalid_csv_format(self):
        """Test error handling with invalid CSV format."""
        # Create CSV with missing required columns
        invalid_data = [
            {"id": 1, "name": "Product 1"},  # Missing category, price, description
        ]
        
        csv_file = self.create_test_csv(invalid_data)
        
        try:
            with pytest.raises(ValueError, match="Missing required columns"):
                MedicalRecommender(csv_file)
        finally:
            Path(csv_file).unlink()

    def test_recommend_with_matching_rules(self):
        """Test recommendation with matching rules."""
        products_data = [
            {"id": 1, "name": "Stethoscope", "category": "sprzet_diagnostyczny", "price": 100.0, "description": "Medical stethoscope"},
            {"id": 2, "name": "Medical Bag", "category": "torby", "price": 200.0, "description": "Doctor's bag"},
            {"id": 3, "name": "Gloves", "category": "higiena", "price": 10.0, "description": "Medical gloves"},
        ]
        
        csv_file = self.create_test_csv(products_data)
        
        try:
            recommender = MedicalRecommender(csv_file)
            recommendation = recommender.recommend("lekarz")
            
            assert recommendation.query == "lekarz"
            assert len(recommendation.products) > 0
            assert recommendation.confidence > 0.5
            assert "lekarz" in recommendation.reasoning.lower() or "sprzęt" in recommendation.reasoning.lower()
            
            # Should recommend products from categories relevant to doctors
            categories = [p.category for p in recommendation.products]
            assert any(cat in ["sprzet_diagnostyczny", "torby", "narzedzia", "wyposazenie"] for cat in categories)
            
        finally:
            Path(csv_file).unlink()

    def test_recommend_with_no_matching_rules(self):
        """Test recommendation with no matching rules (fallback)."""
        products_data = [
            {"id": 1, "name": "Stethoscope", "category": "sprzet_diagnostyczny", "price": 100.0, "description": "Medical stethoscope"},
            {"id": 2, "name": "Gloves", "category": "higiena", "price": 10.0, "description": "Medical gloves"},
        ]
        
        csv_file = self.create_test_csv(products_data)
        
        try:
            recommender = MedicalRecommender(csv_file)
            recommendation = recommender.recommend("xyz unknown profession")
            
            assert recommendation.query == "xyz unknown profession"
            assert len(recommendation.products) > 0
            assert recommendation.confidence < 0.5  # Should have low confidence for fallback
            assert "nie znaleziono" in recommendation.reasoning.lower()
            
        finally:
            Path(csv_file).unlink()

    def test_recommend_empty_query_raises_error(self):
        """Test that empty query raises ValueError."""
        products_data = [
            {"id": 1, "name": "Product 1", "category": "cat1", "price": 10.0, "description": "Desc 1"},
        ]
        
        csv_file = self.create_test_csv(products_data)
        
        try:
            recommender = MedicalRecommender(csv_file)
            
            with pytest.raises(ValueError, match="Query cannot be empty"):
                recommender.recommend("   ")
                
        finally:
            Path(csv_file).unlink()

    def test_get_matching_rules(self):
        """Test getting matching rules for a query."""
        products_data = [
            {"id": 1, "name": "Product 1", "category": "cat1", "price": 10.0, "description": "Desc 1"},
        ]
        
        csv_file = self.create_test_csv(products_data)
        
        try:
            recommender = MedicalRecommender(csv_file)
            
            # Test with query that should match doctor rules
            matching_rules = recommender.get_matching_rules("lekarz")
            
            assert len(matching_rules) > 0
            rule, score = matching_rules[0]
            assert score > 0
            assert "lekarz" in rule.keywords or any("lekarz" in kw for kw in rule.keywords)
            
        finally:
            Path(csv_file).unlink()

    def test_get_products_for_categories(self):
        """Test getting products for specific categories."""
        products_data = [
            {"id": 1, "name": "Product 1", "category": "cat1", "price": 30.0, "description": "Desc 1"},
            {"id": 2, "name": "Product 2", "category": "cat2", "price": 10.0, "description": "Desc 2"},
            {"id": 3, "name": "Product 3", "category": "cat1", "price": 20.0, "description": "Desc 3"},
        ]
        
        csv_file = self.create_test_csv(products_data)
        
        try:
            recommender = MedicalRecommender(csv_file)
            
            # Get products from cat1 only
            products = recommender.get_products_for_categories(["cat1"], limit=10)
            
            assert len(products) == 2
            assert all(p.category == "cat1" for p in products)
            # Should be sorted by price
            assert products[0].price <= products[1].price
            
        finally:
            Path(csv_file).unlink()

    def test_search_products(self):
        """Test searching products by name/description."""
        products_data = [
            {"id": 1, "name": "Stethoscope Medical", "category": "cat1", "price": 100.0, "description": "Doctor tool"},
            {"id": 2, "name": "Surgical Gloves", "category": "cat2", "price": 10.0, "description": "Medical protection"},
            {"id": 3, "name": "Bandage", "category": "cat3", "price": 5.0, "description": "Wound care"},
        ]
        
        csv_file = self.create_test_csv(products_data)
        
        try:
            recommender = MedicalRecommender(csv_file)
            
            # Search by name
            results = recommender.search_products("stethoscope")
            assert len(results) == 1
            assert results[0].name == "Stethoscope Medical"
            
            # Search by description
            results = recommender.search_products("medical")
            assert len(results) == 2  # Should find both stethoscope and gloves
            
            # Case insensitive search
            results = recommender.search_products("SURGICAL")
            assert len(results) == 1
            assert results[0].name == "Surgical Gloves"
            
        finally:
            Path(csv_file).unlink()

    def test_diabetes_specific_recommendation(self):
        """Test specific diabetes-related recommendation."""
        products_data = [
            {"id": 1, "name": "Glukometr", "category": "diabetologia", "price": 150.0, "description": "Blood glucose meter"},
            {"id": 2, "name": "Test strips", "category": "diabetologia", "price": 50.0, "description": "Glucose test strips"},
            {"id": 3, "name": "Stethoscope", "category": "sprzet_diagnostyczny", "price": 200.0, "description": "Medical stethoscope"},
        ]
        
        csv_file = self.create_test_csv(products_data)
        
        try:
            recommender = MedicalRecommender(csv_file)
            recommendation = recommender.recommend("cukrzyca")
            
            assert recommendation.query == "cukrzyca"
            assert len(recommendation.products) > 0
            assert recommendation.confidence > 0.8  # Should be high confidence for specific condition
            
            # Should prioritize diabetology products
            diabetic_products = [p for p in recommendation.products if p.category == "diabetologia"]
            assert len(diabetic_products) > 0
            
        finally:
            Path(csv_file).unlink() 