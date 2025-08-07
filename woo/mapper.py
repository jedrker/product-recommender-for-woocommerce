"""Data mapping utilities for WooCommerce integration."""

import logging
from typing import Any, Dict, List, Optional

from core.models import Product

logger = logging.getLogger(__name__)


class WooCommerceMapper:
    """Maps WooCommerce product data to internal Product models.
    
    Handles conversion from WooCommerce API format to our internal
    product representation with proper category mapping.
    """
    
    # Mapping from WooCommerce categories to our internal categories
    CATEGORY_MAPPING = {
        # Sprzęt diagnostyczny
        "stetoskopy": "sprzet_diagnostyczny",
        "ciśnieniomierze": "sprzet_diagnostyczny", 
        "termometry": "sprzet_diagnostyczny",
        "pulsoksymetry": "sprzet_diagnostyczny",
        "spirometry": "sprzet_diagnostyczny",
        "otoskopy": "sprzet_diagnostyczny",
        "diagnostyka": "sprzet_diagnostyczny",
        "sprzęt diagnostyczny": "sprzet_diagnostyczny",
        
        # Torby i walizki
        "torby medyczne": "torby",
        "walizki ratownicze": "torby",
        "torby": "torby",
        "walizki": "torby",
        
        # Higiena i ochrona osobista
        "rękawice": "higiena",
        "rękawiczki": "higiena",
        "rękawiczki lateksowe": "higiena",
        "rękawiczki nitrylowe": "higiena",
        "rękawiczki winylowe": "higiena",
        "rękawiczki bezpudrowe": "higiena",
        "rękawiczki jałowe": "higiena",
        "maseczki": "higiena",
        "dezynfekcja": "higiena",
        "higiena": "higiena",
        "ochrona osobista": "higiena",
        "czepki": "higiena",
        "czepek": "higiena",
        "fartuchy": "higiena",
        "fartuch": "higiena",
        "ochraniacze": "higiena",
        "kapcie": "higiena",
        "czyściwo": "higiena",
        "ręcznik papierowy": "higiena",
        "płatki": "higiena",
        "waciki": "higiena",
        "płyn": "higiena",
        "płyny": "higiena",
        
        # Diabetologia (tylko produkty dla cukrzyków)
        "glukometry": "diabetologia",
        "paski testowe": "diabetologia",
        "lancety": "diabetologia",
        "insulina": "diabetologia",
        "diabetologia": "diabetologia",
        "cukrzyca": "diabetologia",
        "glukometr": "diabetologia",
        "glikemia": "diabetologia",
        "blood glucose": "diabetologia",
        "test glucose": "diabetologia",
        
        # Suplementy i odżywki
        "cartinorm": "wyposazenie",
        "witamina": "wyposazenie", 
        "suplement": "wyposazenie",
        "kolagen": "wyposazenie",
        "tabletki": "wyposazenie",
        "kapsułki": "wyposazenie",
        "odżywka": "wyposazenie",
        "goodwill": "wyposazenie",
        
        # Opatrunki i materiały opatrunkowe
        "opatrunki": "opatrunki",
        "bandaże": "opatrunki",
        "gaza": "opatrunki",
        "plastry": "opatrunki",
        "materiały opatrunkowe": "opatrunki",
        
        # Sprzęt ratowniczy i medyczny
        "defibrylatory": "sprzet_ratowniczy",
        "aspiratory": "sprzet_ratowniczy",
        "wózki ratownicze": "sprzet_ratowniczy",
        "sprzęt ratowniczy": "sprzet_ratowniczy",
        "ratownictwo": "sprzet_ratowniczy",
        "staza": "sprzet_ratowniczy",
        "aparaty": "sprzet_ratowniczy",
        "aparat": "sprzet_ratowniczy",
        
        # Apteczki i pierwsza pomoc
        "apteczki": "apteczki",
        "pierwsza pomoc": "apteczki",
        "zestawy ratownicze": "apteczki",
        
        # Ortopedia i rehabilitacja
        "ortopedia": "ortopedia",
        "stabilizatory": "ortopedia",
        "kołnierze": "ortopedia",
        "rehabilitacja": "ortopedia",
        "pończochy": "ortopedia",
        "uciskowe": "ortopedia",
        
        # Narzędzia medyczne i chirurgiczne
        "narzędzia chirurgiczne": "narzedzia",
        "nożyczki": "narzedzia",
        "pinzety": "narzedzia",
        "narzędzia": "narzedzia",
        "kaniula": "narzedzia",
        "aplikator": "narzedzia",
        "igły": "narzedzia",
        
        # Materiały jednorazowe i sprzęt medyczny
        "strzykawki": "materialy_jednorazowe",
        "materiały jednorazowe": "materialy_jednorazowe",
        "cewniki": "materialy_jednorazowe",
        "cewnik": "materialy_jednorazowe",
        "sonda": "materialy_jednorazowe",
        "sondy": "materialy_jednorazowe",
        "zgłębnik": "materialy_jednorazowe",
        "koszula": "materialy_jednorazowe",
        "koszule": "materialy_jednorazowe",
        "spódniczki": "materialy_jednorazowe",
        "ubranie operacyjne": "materialy_jednorazowe",
        "kranik": "materialy_jednorazowe",
        "przyrząd": "materialy_jednorazowe",
        "przedłużacz": "materialy_jednorazowe",
        "łącznik": "materialy_jednorazowe",
        "korek": "materialy_jednorazowe",
        "zatyczka": "materialy_jednorazowe",
        "pojemniki": "materialy_jednorazowe",
        "pojemnik": "materialy_jednorazowe",
        "worki": "materialy_jednorazowe",
        "worek": "materialy_jednorazowe",
        "rękaw": "materialy_jednorazowe",
        "rękawy": "materialy_jednorazowe",
        "paski": "materialy_jednorazowe",
        "testy": "materialy_jednorazowe",
        "test": "materialy_jednorazowe",
        "biologiczne": "materialy_jednorazowe",
        "sterylizacja": "materialy_jednorazowe",
        "jałowe": "materialy_jednorazowe",
        "niejałowe": "materialy_jednorazowe",
        "jednorazowe": "materialy_jednorazowe",
        "włóknina": "materialy_jednorazowe",
        "włókninowe": "materialy_jednorazowe",
        "sms": "materialy_jednorazowe",
        "foliowe": "materialy_jednorazowe",
        "papierowe": "materialy_jednorazowe",
        "papierowy": "materialy_jednorazowe",
        
        # Wyposażenie medyczne i sprzęt
        "lampy": "wyposazenie",
        "stoły": "wyposazenie",
        "wyposażenie": "wyposazenie",
        "woda destylowana": "wyposazenie",
        "woda": "wyposazenie",
        "destylowana": "wyposazenie",
        
        # Urologia i produkty dla dorosłych (refundacja NFZ)
        "urologia": "ortopedia",  # Umieszczamy w ortopedii jako produkty rehabilitacyjne
        "urologiczne": "ortopedia",
        "wkładki": "ortopedia",
        "podkłady": "ortopedia",
        "pieluchomajtki": "ortopedia",
        "majtki chłonne": "ortopedia",
        "seni": "ortopedia",
        "refundacja nfz": "ortopedia",
        "refundacja": "ortopedia",
        "nfz": "ortopedia",
        
        # Weterynaryjne (specjalna kategoria)
        "weterynaryjna": "narzedzia",
        "weterynaryjne": "narzedzia",
        "kruuse": "narzedzia",
        "buster": "narzedzia",
        "zwierząt": "narzedzia",
        "zwierzęta": "narzedzia",
    }
    
    # Default category for unmapped products
    DEFAULT_CATEGORY = "sprzet_diagnostyczny"
    
    @classmethod
    def map_woo_product_to_product(cls, woo_product: Dict[str, Any]) -> Product:
        """Map WooCommerce product data to internal Product model.
        
        Args:
            woo_product: Product dictionary from WooCommerce API
            
        Returns:
            Product model instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        try:
            # Extract basic product information
            product_id = int(woo_product.get("id", 0))
            if product_id <= 0:
                raise ValueError("Invalid product ID")
            
            name = woo_product.get("name", "").strip()
            if not name:
                raise ValueError("Product name is required")
            
            # Extract price (handle different price formats)
            price = cls._extract_price(woo_product)
            
            # Extract description
            description = cls._extract_description(woo_product)
            
            # Map category
            category = cls._map_category(woo_product)
            
            return Product(
                id=product_id,
                name=name,
                category=category,
                price=price,
                description=description
            )
            
        except Exception as e:
            logger.error(f"Failed to map WooCommerce product {woo_product.get('id', 'unknown')}: {e}")
            raise ValueError(f"Invalid product data: {e}") from e
    
    @classmethod
    def map_woo_products_to_products(cls, woo_products: List[Dict[str, Any]]) -> List[Product]:
        """Map list of WooCommerce products to internal Product models.
        
        Args:
            woo_products: List of product dictionaries from WooCommerce API
            
        Returns:
            List of Product model instances
            
        Note:
            Invalid products are logged and skipped
        """
        products = []
        skipped_count = 0
        
        for woo_product in woo_products:
            try:
                product = cls.map_woo_product_to_product(woo_product)
                products.append(product)
            except ValueError as e:
                logger.warning(f"Skipping invalid product {woo_product.get('id', 'unknown')}: {e}")
                skipped_count += 1
        
        if skipped_count > 0:
            logger.info(f"Mapped {len(products)} products, skipped {skipped_count} invalid products")
        
        return products
    
    @classmethod
    def _extract_price(cls, woo_product: Dict[str, Any]) -> float:
        """Extract price from WooCommerce product data.
        
        Args:
            woo_product: Product dictionary from WooCommerce API
            
        Returns:
            Product price as float
            
        Raises:
            ValueError: If price is missing or invalid
        """
        # Try different price fields in order of preference
        price_fields = ["price", "regular_price", "sale_price"]
        
        for field in price_fields:
            price_str = woo_product.get(field, "")
            if price_str and price_str != "":
                try:
                    price = float(price_str)
                    if price >= 0:
                        return price
                except (ValueError, TypeError):
                    continue
        
        # If no valid price found, try to extract from price_html
        price_html = woo_product.get("price_html", "")
        if price_html:
            # Simple regex-like extraction (basic implementation)
            import re
            price_match = re.search(r'(\d+[.,]\d+)', price_html)
            if price_match:
                try:
                    price_str = price_match.group(1).replace(',', '.')
                    price = float(price_str)
                    if price >= 0:
                        return price
                except (ValueError, TypeError):
                    pass
        
        raise ValueError("No valid price found")
    
    @classmethod
    def _extract_description(cls, woo_product: Dict[str, Any]) -> str:
        """Extract description from WooCommerce product data.
        
        Args:
            woo_product: Product dictionary from WooCommerce API
            
        Returns:
            Product description
        """
        # Try different description fields
        description_fields = ["description", "short_description", "name"]
        
        for field in description_fields:
            description = woo_product.get(field, "").strip()
            if description:
                # Clean HTML tags if present
                description = cls._clean_html(description)
                if description:
                    return description
        
        return "Brak opisu"
    
    @classmethod
    def _clean_html(cls, text: str) -> str:
        """Remove HTML tags from text.
        
        Args:
            text: Text that may contain HTML tags
            
        Returns:
            Clean text without HTML tags
        """
        import re
        # Simple HTML tag removal
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text).strip()
    
    @classmethod
    def _map_category(cls, woo_product: Dict[str, Any]) -> str:
        """Map WooCommerce categories to internal categories.
        
        Args:
            woo_product: Product dictionary from WooCommerce API
            
        Returns:
            Mapped category name
        """
        # Get categories from WooCommerce product
        categories = woo_product.get("categories", [])
        
        # Extract category names
        category_names = []
        for category in categories:
            name = category.get("name", "").lower().strip()
            if name:
                category_names.append(name)
        
        # Try to map each category
        for category_name in category_names:
            mapped_category = cls.CATEGORY_MAPPING.get(category_name)
            if mapped_category:
                logger.debug(f"Mapped category '{category_name}' to '{mapped_category}'")
                return mapped_category
        
        # If no direct mapping, try partial matches
        for category_name in category_names:
            for woo_cat, internal_cat in cls.CATEGORY_MAPPING.items():
                if woo_cat in category_name or category_name in woo_cat:
                    logger.debug(f"Partial match: '{category_name}' -> '{internal_cat}'")
                    return internal_cat
        
        # Check product name and description for category hints
        name = woo_product.get("name", "").lower()
        description = woo_product.get("description", "").lower()
        text_to_search = f"{name} {description}"
        
        # Score-based matching for better accuracy
        category_scores = {}
        
        for woo_cat, internal_cat in cls.CATEGORY_MAPPING.items():
            score = 0
            woo_cat_lower = woo_cat.lower()
            
            # Exact word match gets highest score
            if f" {woo_cat_lower} " in f" {text_to_search} ":
                score += 10
            # Word at beginning or end
            elif text_to_search.startswith(woo_cat_lower) or text_to_search.endswith(woo_cat_lower):
                score += 8
            # Partial match in word
            elif woo_cat_lower in text_to_search:
                score += 5
            
            # Bonus for longer matches (more specific)
            if score > 0:
                score += len(woo_cat_lower) * 0.1
                
            if score > 0:
                if internal_cat not in category_scores:
                    category_scores[internal_cat] = 0
                category_scores[internal_cat] = max(category_scores[internal_cat], score)
        
        # Return category with highest score
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            logger.debug(f"Best match for '{name}': '{best_category[0]}' (score: {best_category[1]:.1f})")
            return best_category[0]
        
        # Default category
        logger.warning(f"No category mapping found for product '{woo_product.get('name', 'unknown')}', using default")
        return cls.DEFAULT_CATEGORY
    
    @classmethod
    def get_available_categories(cls) -> List[str]:
        """Get list of available internal categories.
        
        Returns:
            List of category names
        """
        return list(set(cls.CATEGORY_MAPPING.values()))
    
    @classmethod
    def get_category_mapping(cls) -> Dict[str, str]:
        """Get the current category mapping.
        
        Returns:
            Dictionary mapping WooCommerce categories to internal categories
        """
        return cls.CATEGORY_MAPPING.copy()
