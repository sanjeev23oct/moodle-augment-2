#!/usr/bin/env python3
"""
Startup script for the Multi-Provider AI Chat API

This script provides an easy way to run the application with different configurations.
"""

import argparse
import sys
import uvicorn
from pathlib import Path

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Multi-Provider AI Chat API")
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--log-level", 
        default="info", 
        choices=["debug", "info", "warning", "error", "critical"],
        help="Log level (default: info)"
    )
    parser.add_argument(
        "--workers", 
        type=int, 
        default=1, 
        help="Number of worker processes (default: 1)"
    )
    
    args = parser.parse_args()
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("Warning: .env file not found. Copy .env.example to .env and configure your API keys.")
        print("The application will start but some providers may not be available.")
        print()
    
    print(f"Starting Multi-Provider AI Chat API...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Log Level: {args.log_level}")
    print(f"Reload: {args.reload}")
    print(f"Workers: {args.workers}")
    print()
    print(f"API Documentation will be available at:")
    print(f"  - Swagger UI: http://{args.host}:{args.port}/docs")
    print(f"  - ReDoc: http://{args.host}:{args.port}/redoc")
    print()
    
    try:
        uvicorn.run(
            "app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            workers=args.workers if not args.reload else 1
        )
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
