#!/usr/bin/env python3
# This is a compatibility wrapper that simply imports the real wrapper
# to maintain compatibility with existing task definitions

import sys
import os
import argparse

# Import the actual wrapper module
from mcp_http_wrapper_customdoc import main

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='MCP HTTP Wrapper')
    parser.add_argument('--port', type=int, default=8005, help='Port to listen on')
    args = parser.parse_args()
    
    # Call the main function from the actual wrapper
    main(port=args.port)
