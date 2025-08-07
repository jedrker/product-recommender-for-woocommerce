"""Test module for core.models."""

import pytest

from core.models import Product, Recommendation, RecommendationRule


class TestProduct:
    """Test cases for Product model."""

    def test_product_creation_valid(self):
        """Test creating a valid product."""
        product = Product(
            id=1,
            name="Test Product",
            category="test_category",
            price=99.99,
            description="Test description"
        )
        
        assert product.id == 1
        assert product.name == "Test Product"
        assert product.category == "test_category"
        assert product.price == 99.99
        assert product.description == "Test description"

    def test_product_negative_price_raises_error(self):
        """Test that negative price raises ValueError."""
        with pytest.raises(ValueError, match="Product price cannot be negative"):
            Product(
                id=1,
                name="Test Product",
                category="test_category",
                price=-10.0,
                description="Test description"
            )

    def test_product_empty_name_raises_error(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Product name cannot be empty"):
            Product(
                id=1,
                name="   ",
                category="test_category",
                price=99.99,
                description="Test description"
            )

    def test_product_empty_category_raises_error(self):
        """Test that empty category raises ValueError."""
        with pytest.raises(ValueError, match="Product category cannot be empty"):
            Product(
                id=1,
                name="Test Product",
                category="",
                price=99.99,
                description="Test description"
            )


class TestRecommendation:
    """Test cases for Recommendation model."""

    def create_sample_products(self):
        """Create sample products for testing."""
        return [
            Product(1, "Product 1", "category1", 10.0, "Description 1"),
            Product(2, "Product 2", "category2", 20.0, "Description 2"),
        ]

    def test_recommendation_creation_valid(self):
        """Test creating a valid recommendation."""
        products = self.create_sample_products()
        recommendation = Recommendation(
            query="test query",
            products=products,
            confidence=0.8,
            reasoning="Test reasoning"
        )
        
        assert recommendation.query == "test query"
        assert len(recommendation.products) == 2
        assert recommendation.confidence == 0.8
        assert recommendation.reasoning == "Test reasoning"

    def test_recommendation_confidence_out_of_range_raises_error(self):
        """Test that confidence out of range raises ValueError."""
        products = self.create_sample_products()
        
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            Recommendation(
                query="test query",
                products=products,
                confidence=1.5,
                reasoning="Test reasoning"
            )

    def test_recommendation_empty_query_raises_error(self):
        """Test that empty query raises ValueError."""
        products = self.create_sample_products()
        
        with pytest.raises(ValueError, match="Query cannot be empty"):
            Recommendation(
                query="   ",
                products=products,
                confidence=0.8,
                reasoning="Test reasoning"
            )

    def test_recommendation_to_dict(self):
        """Test converting recommendation to dictionary."""
        products = self.create_sample_products()
        recommendation = Recommendation(
            query="test query",
            products=products,
            confidence=0.8,
            reasoning="Test reasoning"
        )
        
        result = recommendation.to_dict()
        
        assert result["query"] == "test query"
        assert result["confidence"] == 0.8
        assert result["reasoning"] == "Test reasoning"
        assert len(result["products"]) == 2
        assert result["products"][0]["id"] == 1
        assert result["products"][0]["name"] == "Product 1"


class TestRecommendationRule:
    """Test cases for RecommendationRule model."""

    def test_rule_creation_valid(self):
        """Test creating a valid recommendation rule."""
        rule = RecommendationRule(
            keywords=["test", "keyword"],
            categories=["category1", "category2"],
            weight=0.8,
            description="Test rule"
        )
        
        assert rule.keywords == ["test", "keyword"]
        assert rule.categories == ["category1", "category2"]
        assert rule.weight == 0.8
        assert rule.description == "Test rule"

    def test_rule_empty_keywords_raises_error(self):
        """Test that empty keywords list raises ValueError."""
        with pytest.raises(ValueError, match="Rule must have at least one keyword"):
            RecommendationRule(
                keywords=[],
                categories=["category1"],
                weight=0.8,
                description="Test rule"
            )

    def test_rule_empty_categories_raises_error(self):
        """Test that empty categories list raises ValueError."""
        with pytest.raises(ValueError, match="Rule must have at least one category"):
            RecommendationRule(
                keywords=["test"],
                categories=[],
                weight=0.8,
                description="Test rule"
            )

    def test_rule_negative_weight_raises_error(self):
        """Test that negative weight raises ValueError."""
        with pytest.raises(ValueError, match="Rule weight cannot be negative"):
            RecommendationRule(
                keywords=["test"],
                categories=["category1"],
                weight=-0.1,
                description="Test rule"
            )

    def test_rule_matches_case_insensitive(self):
        """Test that rule matching is case insensitive."""
        rule = RecommendationRule(
            keywords=["Doctor", "MEDIC"],
            categories=["category1"],
            weight=0.8,
            description="Test rule"
        )
        
        assert rule.matches("I am a doctor")
        assert rule.matches("DOCTOR here")
        assert rule.matches("medic needed")
        assert rule.matches("Medical DOCTOR")

    def test_rule_matches_partial_words(self):
        """Test that rule matches keywords within words."""
        rule = RecommendationRule(
            keywords=["medic"],
            categories=["category1"],
            weight=0.8,
            description="Test rule"
        )
        
        assert rule.matches("paramedic")
        assert rule.matches("medical")
        assert rule.matches("medication")

    def test_rule_no_match(self):
        """Test that rule doesn't match unrelated queries."""
        rule = RecommendationRule(
            keywords=["doctor", "medic"],
            categories=["category1"],
            weight=0.8,
            description="Test rule"
        )
        
        assert not rule.matches("engineer")
        assert not rule.matches("teacher")
        assert not rule.matches("lawyer") 