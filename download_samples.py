#!/usr/bin/env python3
"""
Download sample PNG files for testing the PNG to ICO Converter.
"""

import os
import urllib.request
from pathlib import Path

def download_sample(url, filename):
    """Download a sample file."""
    try:
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filename)
        print(f"✓ Downloaded {filename}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {filename}: {e}")
        return False

def main():
    """Download sample PNG files."""
    # Create sample_data directory
    sample_dir = Path("sample_data")
    sample_dir.mkdir(exist_ok=True)

    # Sample PNG files to download
    samples = [
        ("https://picsum.photos/256/256?random=1", "sample_1.png"),
        ("https://picsum.photos/128/128?random=2", "sample_2.png"),
        ("https://picsum.photos/64/64?random=3", "sample_3.png"),
        ("https://picsum.photos/32/32?random=4", "sample_4.png"),
    ]

    print("Downloading sample PNG files for testing...")

    downloaded = 0
    for url, filename in samples:
        filepath = sample_dir / filename
        if filepath.exists():
            print(f"✓ {filename} already exists")
            downloaded += 1
        elif download_sample(url, filepath):
            downloaded += 1

    print(f"\nDownloaded {downloaded}/{len(samples)} sample files")
    print("Sample files are in the 'sample_data' directory")

if __name__ == "__main__":
    main()