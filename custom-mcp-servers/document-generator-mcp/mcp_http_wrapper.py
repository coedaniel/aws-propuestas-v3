#!/usr/bin/env python3
# This is a compatibility wrapper that simply imports the real wrapper
# to maintain compatibility with existing Dockerfiles

import sys
import os

# Import the actual wrapper
from mcp_http_wrapper_customdoc import main

if __name__ == "__main__":
    main()
