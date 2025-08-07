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
        "--json", "-j",
        action="store_true",
        help="Wyświetl wyniki w formacie JSON"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Włącz szczegółowe logowanie"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Print banner for interactive mode
    if not args.query:
        print_banner()
    
    try:
        # Initialize recommender
        recommender = MedicalRecommender(args.products)
        
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