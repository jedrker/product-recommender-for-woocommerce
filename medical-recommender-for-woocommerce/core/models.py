"""Data models for the medical product recommendation system."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Product:
    """Represents a medical product.
    
    Attributes:
        id: Unique product identifier
        name: Product name
        category: Product category (e.g., 'torby', 'sprzet_diagnostyczny')
        price: Product price in PLN
        description: Product description
    """
    id: int
    name: str
    category: str
    price: float
    description: str

    def __post_init__(self) -> None:
        """Validate product data after initialization."""
        if self.price < 0:
            raise ValueError("Product price cannot be negative")
        if not self.name.strip():
            raise ValueError("Product name cannot be empty")
        if not self.category.strip():
            raise ValueError("Product category cannot be empty")


@dataclass
class Recommendation:
    """Represents a product recommendation result.
    
    Attributes:
        query: Original user query (profession or health condition)
        products: List of recommended products
        confidence: Confidence score (0.0 to 1.0)
        reasoning: Explanation of why these products were recommended
    """
    query: str
    products: List[Product]
    confidence: float
    reasoning: str

    def __post_init__(self) -> None:
        """Validate recommendation data after initialization."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        if not self.query.strip():
            raise ValueError("Query cannot be empty")

    def to_dict(self) -> dict:
        """Convert recommendation to dictionary format.
        
        Returns:
            Dictionary representation of the recommendation
        """
        return {
            "query": self.query,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "products": [
                {
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "price": product.price,
                    "description": product.description,
                }
                for product in self.products
            ],
        }


@dataclass
class RecommendationRule:
    """Represents a recommendation rule mapping user input to product categories.
    
    Attributes:
        keywords: List of keywords that trigger this rule
        categories: List of product categories to recommend
        weight: Rule weight/priority (higher = more important)
        description: Human-readable description of the rule
    """
    keywords: List[str]
    categories: List[str]
    weight: float
    description: str

    def __post_init__(self) -> None:
        """Validate rule data after initialization."""
        if not self.keywords:
            raise ValueError("Rule must have at least one keyword")
        if not self.categories:
            raise ValueError("Rule must have at least one category")
        if self.weight < 0:
            raise ValueError("Rule weight cannot be negative")

    def matches(self, query: str) -> bool:
        """Check if this rule matches the given query.
        
        Args:
            query: User input to check against keywords
            
        Returns:
            True if any keyword is found in the query (case-insensitive)
        """
        query_lower = query.lower()
        return any(keyword.lower() in query_lower for keyword in self.keywords) 