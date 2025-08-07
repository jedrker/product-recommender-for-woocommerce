"""Main recommendation engine for medical products.

This module contains the core logic for generating product recommendations
based on user input and business rules.
"""

import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd

from core.models import Product, Recommendation, RecommendationRule
from core.rules import get_recommendation_rules, get_fallback_categories


logger = logging.getLogger(__name__)


class MedicalRecommender:
    """Main recommendation engine for medical products."""

    def __init__(self, products_file: Optional[str] = None):
        """Initialize the recommender with product data.
        
        Args:
            products_file: Path to CSV file with products. 
                         If None, uses default data/products.csv
        """
        self.products: List[Product] = []
        self.rules: List[RecommendationRule] = get_recommendation_rules()
        self._products_by_category: Dict[str, List[Product]] = {}
        
        if products_file is None:
            # Default path relative to project root
            project_root = Path(__file__).parent.parent
            products_file = project_root / "data" / "products.csv"
        
        self.load_products(products_file)

    def load_products(self, file_path: Union[str, Path]) -> None:
        """Load products from CSV file.
        
        Args:
            file_path: Path to the CSV file containing product data
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If the CSV file has invalid format or data
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Products file not found: {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            required_columns = {"id", "name", "category", "price", "description"}
            
            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                raise ValueError(f"Missing required columns: {missing}")
            
            self.products = []
            for _, row in df.iterrows():
                product = Product(
                    id=int(row["id"]),
                    name=str(row["name"]),
                    category=str(row["category"]),
                    price=float(row["price"]),
                    description=str(row["description"])
                )
                self.products.append(product)
            
            # Group products by category for faster lookup
            self._group_products_by_category()
            
            logger.info(f"Loaded {len(self.products)} products from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading products from {file_path}: {e}")
            raise ValueError(f"Failed to load products: {e}") from e

    def _group_products_by_category(self) -> None:
        """Group products by category for efficient lookup."""
        self._products_by_category = {}
        for product in self.products:
            if product.category not in self._products_by_category:
                self._products_by_category[product.category] = []
            self._products_by_category[product.category].append(product)

    def get_matching_rules(self, query: str) -> List[Tuple[RecommendationRule, float]]:
        """Find rules that match the given query.
        
        Args:
            query: User input to match against rules
            
        Returns:
            List of tuples (rule, score) sorted by score descending
        """
        matching_rules = []
        
        for rule in self.rules:
            if rule.matches(query):
                # Calculate score based on rule weight and keyword match strength
                score = rule.weight
                
                # Bonus for exact keyword matches
                query_lower = query.lower()
                exact_matches = sum(1 for keyword in rule.keywords 
                                  if keyword.lower() == query_lower)
                if exact_matches > 0:
                    score *= (1 + exact_matches * 0.2)
                
                matching_rules.append((rule, score))
        
        # Sort by score descending
        matching_rules.sort(key=lambda x: x[1], reverse=True)
        return matching_rules

    def get_products_for_categories(self, categories: List[str], limit: int = 10) -> List[Product]:
        """Get products from specified categories.
        
        Args:
            categories: List of category names to search
            limit: Maximum number of products to return
            
        Returns:
            List of products, sorted by price ascending
        """
        products = []
        
        for category in categories:
            if category in self._products_by_category:
                products.extend(self._products_by_category[category])
        
        # Remove duplicates and sort by price
        unique_products = list({p.id: p for p in products}.values())
        unique_products.sort(key=lambda p: p.price)
        
        return unique_products[:limit]

    def recommend(self, query: str, max_products: int = 10) -> Recommendation:
        """Generate product recommendations for the given query.
        
        Args:
            query: User input (profession, health condition, etc.)
            max_products: Maximum number of products to recommend
            
        Returns:
            Recommendation object with products and metadata
        """
        if not query.strip():
            raise ValueError("Query cannot be empty")
        
        logger.info(f"Generating recommendations for query: '{query}'")
        
        # Find matching rules
        matching_rules = self.get_matching_rules(query)
        
        if not matching_rules:
            # No specific rules matched, use fallback
            logger.info(f"No specific rules matched for '{query}', using fallback")
            categories = get_fallback_categories()
            confidence = 0.3
            reasoning = "Nie znaleziono specyficznych reguł. Pokazuję podstawowe produkty medyczne."
        else:
            # Extract categories from matching rules
            categories = []
            total_weight = 0
            rule_descriptions = []
            
            for rule, score in matching_rules:
                categories.extend(rule.categories)
                total_weight += score
                rule_descriptions.append(rule.description)
            
            # Remove duplicates while preserving order
            categories = list(dict.fromkeys(categories))
            
            # Calculate confidence based on rule weights and matches
            confidence = min(0.95, total_weight / len(matching_rules))
            reasoning = f"Rekomendacje na podstawie: {'; '.join(rule_descriptions[:2])}"
        
        # Get products for recommended categories
        recommended_products = self.get_products_for_categories(categories, max_products)
        
        if not recommended_products:
            logger.warning(f"No products found for categories: {categories}")
            # Emergency fallback - get any products
            recommended_products = self.products[:max_products]
            confidence = 0.1
            reasoning = "Brak produktów w rekomendowanych kategoriach. Pokazuję dostępne produkty."
        
        logger.info(f"Generated {len(recommended_products)} recommendations with confidence {confidence:.2f}")
        
        return Recommendation(
            query=query,
            products=recommended_products,
            confidence=confidence,
            reasoning=reasoning
        )

    def get_categories(self) -> List[str]:
        """Get all available product categories.
        
        Returns:
            List of unique category names
        """
        return list(self._products_by_category.keys())

    def get_products_count(self) -> int:
        """Get total number of loaded products.
        
        Returns:
            Number of products in the system
        """
        return len(self.products)

    def search_products(self, search_term: str, limit: int = 20) -> List[Product]:
        """Search products by name or description.
        
        Args:
            search_term: Term to search for in product name/description
            limit: Maximum number of results
            
        Returns:
            List of matching products
        """
        search_term = search_term.lower()
        matching_products = []
        
        for product in self.products:
            if (search_term in product.name.lower() or 
                search_term in product.description.lower()):
                matching_products.append(product)
        
        return matching_products[:limit] 