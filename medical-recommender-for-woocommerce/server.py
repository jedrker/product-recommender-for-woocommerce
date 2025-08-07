#!/usr/bin/env python3
"""Entry point for running the Flask API server."""

import argparse
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api.app import create_app


def main() -> None:
    """Main entry point for the server."""
    parser = argparse.ArgumentParser(
        description="Medical Product Recommender API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                      # Run with default settings
  %(prog)s --env .env          # Use specific env file
  %(prog)s --port 8000         # Run on port 8000
  %(prog)s --host 127.0.0.1    # Bind to localhost only
  %(prog)s --debug             # Enable debug mode
        """
    )
    
    parser.add_argument(
        '--env', 
        type=str, 
        help='Path to environment file (default: .env)'
    )
    parser.add_argument(
        '--host', 
        type=str, 
        default='0.0.0.0',
        help='Host to bind the server to (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=5000,
        help='Port to run the server on (default: 5000)'
    )
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Enable debug mode'
    )
    parser.add_argument(
        '--no-reload', 
        action='store_true',
        help='Disable auto-reload in debug mode'
    )
    
    args = parser.parse_args()
    
    # Create Flask app
    try:
        app = create_app(config_path=args.env)
        
        # Configure app based on arguments
        app.config['DEBUG'] = args.debug
        
        print(f"🏥 Medical Product Recommender API")
        print(f"📡 Server starting on http://{args.host}:{args.port}")
        print(f"🔧 Debug mode: {'ON' if args.debug else 'OFF'}")
        
        if args.env:
            print(f"⚙️  Using config: {args.env}")
        
        print("\n📚 Available endpoints:")
        print(f"  GET  http://{args.host}:{args.port}/")
        print(f"  GET  http://{args.host}:{args.port}/recommend?input=<query>")
        print(f"  GET  http://{args.host}:{args.port}/products")
        print(f"  GET  http://{args.host}:{args.port}/categories")
        print("\n🚀 Server ready! Press Ctrl+C to stop.\n")
        
        # Run the server
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            use_reloader=args.debug and not args.no_reload,
            threaded=True
        )
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
