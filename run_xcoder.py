#!/usr/bin/env python3
"""
Simple XCoder launcher - just run this file to start XCoder CLI
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    from cli.xcoder_cli import main
    main()