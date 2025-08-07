"""Configuration management for the medical recommender system."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


class Config:
    """Configuration manager for the application.
    
    Loads configuration from environment variables and .env file.
    Provides default values for missing configuration.
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            env_file: Path to .env file. If None, looks for .env in project root.
        """
        if env_file is None:
            # Look for .env in project root
            project_root = Path(__file__).parent.parent
            env_file = project_root / ".env"
        
        # Load environment variables from .env file if it exists
        if Path(env_file).exists():
            load_dotenv(env_file)
        
        # WooCommerce API settings
        self.woocommerce_url = self._get_env("WOOCOMMERCE_URL", "")
        self.woocommerce_consumer_key = self._get_env("WOOCOMMERCE_CONSUMER_KEY", "")
        self.woocommerce_consumer_secret = self._get_env("WOOCOMMERCE_CONSUMER_SECRET", "")
        
        # Cache settings
        self.cache_duration = int(self._get_env("CACHE_DURATION", "3600"))
        
        # API settings
        self.max_products = int(self._get_env("MAX_PRODUCTS", "100"))
        self.api_timeout = int(self._get_env("API_TIMEOUT", "30"))
        
        # Logging
        self.log_level = self._get_env("LOG_LEVEL", "INFO")
    
    def _get_env(self, key: str, default: str) -> str:
        """Get environment variable with fallback to default.
        
        Args:
            key: Environment variable name
            default: Default value if variable not set
            
        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)
    
    def is_woocommerce_configured(self) -> bool:
        """Check if WooCommerce API is properly configured.
        
        Returns:
            True if all required WooCommerce settings are present
        """
        return all([
            self.woocommerce_url,
            self.woocommerce_consumer_key,
            self.woocommerce_consumer_secret
        ])
    
    def get_woocommerce_base_url(self) -> str:
        """Get base URL for WooCommerce API.
        
        Returns:
            Base URL for WooCommerce REST API
            
        Raises:
            ValueError: If WooCommerce URL is not configured
        """
        if not self.woocommerce_url:
            raise ValueError("WOOCOMMERCE_URL not configured")
        
        # Ensure URL doesn't end with slash
        base_url = self.woocommerce_url.rstrip('/')
        return f"{base_url}/wp-json/wc/v3"
    
    def validate(self) -> None:
        """Validate configuration and raise errors for missing required settings.
        
        Raises:
            ValueError: If required settings are missing
        """
        errors = []
        
        if not self.woocommerce_url:
            errors.append("WOOCOMMERCE_URL is required")
        
        if not self.woocommerce_consumer_key:
            errors.append("WOOCOMMERCE_CONSUMER_KEY is required")
        
        if not self.woocommerce_consumer_secret:
            errors.append("WOOCOMMERCE_CONSUMER_SECRET is required")
        
        if self.cache_duration < 0:
            errors.append("CACHE_DURATION must be non-negative")
        
        if self.max_products < 1:
            errors.append("MAX_PRODUCTS must be at least 1")
        
        if self.api_timeout < 1:
            errors.append("API_TIMEOUT must be at least 1")
        
        if errors:
            raise ValueError(f"Configuration errors: {'; '.join(errors)}")
    
    def __str__(self) -> str:
        """String representation of configuration (without sensitive data)."""
        return (
            f"Config("
            f"woocommerce_url={self.woocommerce_url}, "
            f"cache_duration={self.cache_duration}s, "
            f"max_products={self.max_products}, "
            f"api_timeout={self.api_timeout}s, "
            f"log_level={self.log_level}"
            f")"
        )
