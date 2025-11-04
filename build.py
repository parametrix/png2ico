#!/usr/bin/env python3
"""
Convenience build script for PNG to ICO Converter
Runs the comprehensive build script.
"""

import sys
import os
from pathlib import Path

def main():
    """Run the build script."""
    # Get the directory of this script
    script_dir = Path(__file__).parent

    # Path to the comprehensive build script
    build_script = script_dir / "build" / "build.py"

    if not build_script.exists():
        print("Error: Build script not found at", build_script)
        sys.exit(1)

    # Change to the build script directory and run it
    os.chdir(build_script.parent)
    os.system(f"{sys.executable} build.py {' '.join(sys.argv[1:])}")

if __name__ == "__main__":
    main()