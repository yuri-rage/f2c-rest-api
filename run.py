#!/usr/bin/env python3

import uvicorn
import argparse
from app.main import app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fields2Cover REST API Server",
        epilog="Example: python run.py --port 8080",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="port number for the API server (default: 8000)",
    )
    args = parser.parse_args()

    uvicorn.run(app, host="0.0.0.0", port=args.port)
