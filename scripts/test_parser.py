#!/usr/bin/env python3
"""Test script for OpenMUSIC parser on example files.

This script extracts and parses all .sqz files in data/example
and outputs a summary of what was found.
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from openmusic import SQZExtractor, MusicFileParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_file(sqz_path: Path) -> dict:
    """Test parsing a single .sqz file."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing: {sqz_path.name}")
    logger.info(f"{'='*60}")

    try:
        # Extract the SQZ file
        with SQZExtractor() as extractor:
            music_data_file = extractor.extract(sqz_path)

            # Parse the extracted file
            parser = MusicFileParser(music_data_file)
            model = parser.parse()

            # Output summary
            logger.info(f"File version: {model.version}")
            logger.info(f"Nodes found: {len(model.nodes)}")

            # Count node types
            node_types = {}
            for node in model.nodes:
                node_types[node.node_type] = node_types.get(node.node_type, 0) + 1
                logger.info(f"  - {node.node_type}: {node.name} at ({node.x:.1f}, {node.y:.1f})")

            logger.info(f"Node type summary: {node_types}")

            return {
                'file': sqz_path.name,
                'version': model.version,
                'nodes': len(model.nodes),
                'node_types': node_types,
                'success': True,
            }

    except Exception as e:
        logger.error(f"Failed to parse {sqz_path.name}: {e}")
        return {
            'file': sqz_path.name,
            'error': str(e),
            'success': False,
        }


def main():
    """Run tests on all example files."""
    example_dir = Path(__file__).parent.parent / "data" / "example"

    # Find all .sqz files
    sqz_files = list(example_dir.glob("*.sqz"))

    if not sqz_files:
        logger.error(f"No .sqz files found in {example_dir}")
        return 1

    logger.info(f"Found {len(sqz_files)} .sqz files to test")

    results = []
    for sqz_file in sorted(sqz_files):
        result = test_file(sqz_file)
        results.append(result)

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("SUMMARY")
    logger.info(f"{'='*60}")

    success_count = sum(1 for r in results if r['success'])
    logger.info(f"Successful: {success_count}/{len(results)}")

    for r in results:
        status = "OK" if r['success'] else "FAIL"
        logger.info(f"  [{status}] {r['file']}")

    return 0 if success_count == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
