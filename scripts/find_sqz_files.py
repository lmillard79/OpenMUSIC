#!/usr/bin/env python3
"""Background-friendly scanner for MUSIC .sqz files on J and V drives.

This script searches J: and V: drives for .sqz files with low CPU priority
to minimize impact on other work. Results are saved to CSV for analysis.
"""

import os
import sys
import csv
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_sqz_files(drive_letter: str, max_depth: int = 20) -> List[Dict]:
    """Recursively find .sqz files on a drive.

    Args:
        drive_letter: Drive letter (e.g., 'J', 'V')
        max_depth: Maximum directory depth to search

    Returns:
        List of dictionaries containing file information.
    """
    drive_path = Path(f"{drive_letter}:/")
    results = []

    if not drive_path.exists():
        logger.warning(f"Drive {drive_path} does not exist. Skipping.")
        return results

    logger.info(f"Scanning {drive_path}...")
    start_time = time.time()

    try:
        # Use rglob for recursive search
        for i, sqz_file in enumerate(drive_path.rglob("*.sqz")):
            try:
                stat = sqz_file.stat()
                results.append({
                    'file_path': str(sqz_file),
                    'file_name': sqz_file.name,
                    'size_bytes': stat.st_size,
                    'size_kb': round(stat.st_size / 1024, 2),
                    'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'drive': drive_letter,
                    'directory': str(sqz_file.parent),
                })

                # Progress indicator every 100 files
                if (i + 1) % 100 == 0:
                    logger.info(f"  Found {i + 1} files so far...")

            except (OSError, PermissionError) as e:
                # Skip files we can't access
                logger.debug(f"Cannot access {sqz_file}: {e}")
                continue

    except PermissionError as e:
        logger.error(f"Permission denied scanning {drive_path}: {e}")

    elapsed = time.time() - start_time
    logger.info(f"Drive {drive_letter}: found {len(results)} files in {elapsed:.1f}s")

    return results


def set_low_priority():
    """Set process to low priority to be background-friendly."""
    try:
        import psutil
        process = psutil.Process()
        process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if os.name == 'nt' else 10)
        logger.info("Process priority set to BELOW_NORMAL")
    except ImportError:
        logger.warning("psutil not installed - cannot set process priority")
    except Exception as e:
        logger.warning(f"Could not set process priority: {e}")


def save_results(results: List[Dict], output_path: Path) -> None:
    """Save scan results to CSV file."""
    if not results:
        logger.warning("No results to save")
        return

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    logger.info(f"Results saved to: {output_path}")


def print_summary(results: List[Dict]) -> None:
    """Print summary statistics of found files."""
    if not results:
        logger.info("No .sqz files found.")
        return

    print("\n" + "="*60)
    print("SCAN SUMMARY")
    print("="*60)

    # By drive
    print("\nBy drive:")
    drives = {}
    for r in results:
        drives[r['drive']] = drives.get(r['drive'], 0) + 1
    for drive, count in sorted(drives.items()):
        print(f"  {drive}: drive - {count} files")

    # Largest files
    print("\nLargest files:")
    sorted_by_size = sorted(results, key=lambda x: x['size_bytes'], reverse=True)[:5]
    for r in sorted_by_size:
        print(f"  {r['size_kb']:,.0f} KB - {r['file_name']}")

    # Most recent
    print("\nMost recently modified:")
    sorted_by_date = sorted(results, key=lambda x: x['last_modified'], reverse=True)[:5]
    for r in sorted_by_date:
        mod_date = r['last_modified'][:10]  # YYYY-MM-DD
        print(f"  {mod_date} - {r['file_name']}")


def main():
    """Run the background scan."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Background scan for MUSIC .sqz files"
    )
    parser.add_argument(
        '--output', '-o',
        default='d:\\GitRepos\\OpenMUSIC\\data\\sqz_inventory.csv',
        help='Output CSV file path'
    )
    parser.add_argument(
        '--drives', '-d',
        default='J,V',
        help='Comma-separated drive letters to scan (default: J,V)'
    )
    parser.add_argument(
        '--priority', '-p',
        action='store_true',
        default=True,
        help='Set low process priority (default: True)'
    )

    args = parser.parse_args()

    # Set low priority
    if args.priority:
        set_low_priority()

    start_time = time.time()
    logger.info("Starting background scan for .sqz files...")
    logger.info(f"Output: {args.output}")

    # Scan each drive
    all_results = []
    drives = [d.strip().upper() for d in args.drives.split(',')]

    for drive in drives:
        results = find_sqz_files(drive)
        all_results.extend(results)

    # Save and summarize
    output_path = Path(args.output)
    save_results(all_results, output_path)
    print_summary(all_results)

    elapsed = time.time() - start_time
    logger.info(f"\nScan complete in {elapsed:.1f} seconds")
    logger.info(f"Total files found: {len(all_results)}")

    return 0 if all_results else 1


if __name__ == '__main__':
    sys.exit(main())
