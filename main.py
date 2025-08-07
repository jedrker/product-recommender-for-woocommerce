#!/usr/bin/env python3
"""Command-line interface for the Medical Recommender system.

This script provides an interactive CLI for testing the recommendation system
and exploring its capabilities.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from core.recommender import MedicalRecommender
from utils.config import Config


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application.
    
    Args:
        verbose: Enable debug-level logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def print_banner() -> None:
    """Print application banner."""
    print("=" * 60)
    print("🏥 Medical Product Recommender for WooCommerce")
    print("=" * 60)
    print()


def print_recommendation(recommendation, show_json: bool = False) -> None:
    """Print recommendation results in a formatted way.
    
    Args:
        recommendation: Recommendation object to display
        show_json: Whether to show JSON format instead of formatted output
    """
    if show_json:
        print(json.dumps(recommendation.to_dict(), indent=2, ensure_ascii=False))
        return
    
    print(f"\n🔍 Zapytanie: '{recommendation.query}'")
    print(f"🎯 Pewność: {recommendation.confidence:.1%}")
    print(f"💡 Uzasadnienie: {recommendation.reasoning}")
    print(f"\n📦 Rekomendowane produkty ({len(recommendation.products)}):")
    print("-" * 50)
    
    for i, product in enumerate(recommendation.products, 1):
        print(f"{i:2d}. {product.name}")
        print(f"    Kategoria: {product.category}")
        print(f"    Cena: {product.price:.2f} PLN")
        print(f"    Opis: {product.description}")
        print()


def interactive_mode(recommender: MedicalRecommender) -> None:
    """Run interactive CLI mode.
    
    Args:
        recommender: Initialized recommender instance
    """
    print("🚀 Tryb interaktywny - wpisz zapytanie lub 'quit' aby wyjść")
    print("📝 Przykłady: 'ratownik medyczny', 'cukrzyca', 'lekarz', 'pierwsza pomoc'")
    print()
    
    while True:
        try:
            query = input("❓ Twoje zapytanie: ").strip()
            
            if not query:
                continue
                
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Do widzenia!")
                break
            
            if query.lower() == 'help':
                print_help_commands()
                continue
            
            if query.lower() == 'stats':
                print_stats(recommender)
                continue
            
            if query.lower() == 'categories':
                print_categories(recommender)
                continue
            
            if query.lower() == 'refresh':
                print_refresh_products(recommender)
                continue
            
            if query.lower() == 'cache':
                print_cache_info(recommender)
                continue
            
            if query.lower() == 'woo':
                print_woocommerce_info(recommender)
                continue
            
            if query.lower() == 'total':
                print_total_products(recommender)
                continue
            
            # Generate recommendation
            recommendation = recommender.recommend(query)
            print_recommendation(recommendation)
            
        except KeyboardInterrupt:
            print("\n👋 Do widzenia!")
            break
        except Exception as e:
            print(f"❌ Błąd: {e}")


def print_help_commands() -> None:
    """Print available commands."""
    print("\n📚 Dostępne komendy:")
    print("  help       - Pokaż tę pomoc")
    print("  stats      - Pokaż statystyki systemu")
    print("  categories - Pokaż dostępne kategorie")
    print("  refresh    - Odśwież produkty z WooCommerce")
    print("  cache      - Informacje o cache")
    print("  woo        - Informacje o WooCommerce")
    print("  total      - Sprawdź rzeczywistą liczbę produktów w WooCommerce")
    print("  quit/exit  - Wyjdź z programu")
    print()


def print_stats(recommender: MedicalRecommender) -> None:
    """Print system statistics.
    
    Args:
        recommender: Recommender instance
    """
    print(f"\n📊 Statystyki systemu:")
    print(f"  Produkty: {recommender.get_products_count()}")
    print(f"  Kategorie: {len(recommender.get_categories())}")
    print(f"  Reguły: {len(recommender.rules)}")
    
    # WooCommerce info
    if recommender.woo_client:
        print(f"  WooCommerce: ✅ Skonfigurowany")
        if recommender.test_woocommerce_connection():
            print(f"  Połączenie: ✅ Aktywne")
        else:
            print(f"  Połączenie: ❌ Błąd")
    else:
        print(f"  WooCommerce: ❌ Nie skonfigurowany")
    
    print()


def print_categories(recommender: MedicalRecommender) -> None:
    """Print available categories.
    
    Args:
        recommender: Recommender instance
    """
    categories = recommender.get_categories()
    print(f"\n📂 Dostępne kategorie ({len(categories)}):")
    for category in sorted(categories):
        count = len(recommender._products_by_category[category])
        print(f"  • {category} ({count} produktów)")
    print()


def print_refresh_products(recommender: MedicalRecommender) -> None:
    """Refresh products from WooCommerce.
    
    Args:
        recommender: Recommender instance
    """
    if not recommender.woo_client:
        print("❌ WooCommerce nie jest skonfigurowany")
        return
    
    print("🔄 Odświeżanie produktów z WooCommerce...")
    if recommender.refresh_products():
        print(f"✅ Odświeżono {recommender.get_products_count()} produktów")
    else:
        print("❌ Błąd podczas odświeżania produktów")
    print()


def print_cache_info(recommender: MedicalRecommender) -> None:
    """Print cache information.
    
    Args:
        recommender: Recommender instance
    """
    cache_info = recommender.get_cache_info()
    
    if cache_info:
        print(f"\n💾 Informacje o cache:")
        print(f"  Produkty: {cache_info['product_count']}")
        print(f"  Wiek: {cache_info['age_human']}")
        print(f"  Ważność: {'✅ Ważny' if cache_info['is_valid'] else '❌ Wygasł'}")
        print(f"  Czas cache: {cache_info['cache_duration']}s")
    else:
        print(f"\n💾 Cache: Brak danych")
    print()


def print_woocommerce_info(recommender: MedicalRecommender) -> None:
    """Print WooCommerce information.
    
    Args:
        recommender: Recommender instance
    """
    if not recommender.woo_client:
        print("❌ WooCommerce nie jest skonfigurowany")
        return
    
    print(f"\n🛒 Informacje o WooCommerce:")
    
    # Test connection
    if recommender.test_woocommerce_connection():
        print(f"  Połączenie: ✅ Aktywne")
    else:
        print(f"  Połączenie: ❌ Błąd")
    
    # Store info
    store_info = recommender.get_woocommerce_store_info()
    if store_info:
        print(f"  Sklep: {store_info.get('name', 'Nieznany')}")
        print(f"  URL: {store_info.get('url', 'Nieznany')}")
        print(f"  Wersja: {store_info.get('version', 'Nieznana')}")
    else:
        print(f"  Sklep: Nie można pobrać informacji")
    
    print()


def print_total_products(recommender: MedicalRecommender) -> None:
    """Print total number of products in WooCommerce store.
    
    Args:
        recommender: Recommender instance
    """
    if not recommender.woo_client:
        print("❌ WooCommerce nie jest skonfigurowany")
        return
    
    print("🔍 Sprawdzanie rzeczywistej liczby produktów w WooCommerce...")
    
    try:
        total = recommender.get_woocommerce_total_products()
        if total is not None:
            current_limit = recommender.config.max_products if recommender.config else "nieznany"
            print(f"\n📊 Rzeczywista liczba produktów w WooCommerce:")
            print(f"  Wszystkich produktów: {total:,}")
            print(f"  Aktualny limit MAX_PRODUCTS: {current_limit}")
            if isinstance(current_limit, int) and total > current_limit:
                print(f"  ⚠️  W sklepie jest {total - current_limit:,} więcej produktów niż aktualny limit!")
            print()
        else:
            print("❌ Nie udało się pobrać informacji o liczbie produktów")
    except Exception as e:
        print(f"❌ Błąd podczas sprawdzania liczby produktów: {e}")


def single_query_mode(recommender: MedicalRecommender, query: str, 
                     json_output: bool = False) -> None:
    """Process single query and exit.
    
    Args:
        recommender: Initialized recommender instance
        query: Query to process
        json_output: Output in JSON format
    """
    try:
        recommendation = recommender.recommend(query)
        print_recommendation(recommendation, show_json=json_output)
    except Exception as e:
        if json_output:
            error_response = {"error": str(e), "query": query}
            print(json.dumps(error_response, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Błąd: {e}")
        sys.exit(1)


def main() -> None:
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Medical Product Recommender - System rekomendacji produktów medycznych",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  %(prog)s                           # Tryb interaktywny
  %(prog)s --query "ratownik"        # Pojedyncze zapytanie
  %(prog)s --query "cukrzyca" --json # Wynik w formacie JSON
  %(prog)s --products custom.csv     # Własny plik z produktami
  %(prog)s --env .env                # Własny plik konfiguracyjny
        """
    )
    
    parser.add_argument(
        "--query", "-q",
        help="Pojedyncze zapytanie do przetworzenia"
    )
    
    parser.add_argument(
        "--products", "-p",
        help="Ścieżka do pliku CSV z produktami (domyślnie: data/products.csv)"
    )
    
    parser.add_argument(
        "--env", "-e",
        help="Ścieżka do pliku .env z konfiguracją WooCommerce"
    )
    
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Wyświetl wyniki w formacie JSON"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Włącz szczegółowe logowanie"
    )
    
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Wymuś odświeżenie produktów z WooCommerce"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Load configuration
    config = None
    if args.env:
        try:
            config = Config(args.env)
            config.validate()
            logging.info(f"Loaded configuration from {args.env}")
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}")
            sys.exit(1)
    else:
        try:
            config = Config()
            if config.is_woocommerce_configured():
                logging.info("WooCommerce configuration found")
            else:
                logging.info("No WooCommerce configuration, using local data only")
        except Exception as e:
            logging.warning(f"Configuration error: {e}")
            config = None
    
    # Print banner for interactive mode
    if not args.query:
        print_banner()
    
    try:
        # Initialize recommender
        recommender = MedicalRecommender(args.products, config)
        
        # Force refresh if requested
        if args.refresh and config and config.is_woocommerce_configured():
            print("🔄 Wymuszanie odświeżenia produktów z WooCommerce...")
            if recommender.refresh_products():
                print(f"✅ Odświeżono {recommender.get_products_count()} produktów")
            else:
                print("❌ Błąd podczas odświeżania")
                sys.exit(1)
        
        if args.query:
            # Single query mode
            single_query_mode(recommender, args.query, args.json)
        else:
            # Interactive mode
            interactive_mode(recommender)
            
    except FileNotFoundError as e:
        print(f"❌ Błąd: {e}")
        print("💡 Sprawdź czy plik z produktami istnieje lub użyj --products")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Nieoczekiwany błąd: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 