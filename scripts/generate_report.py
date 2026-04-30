#!/usr/bin/env python3
"""Generate structured report sections from MUSIC .sqz files.

This tool extracts everything from a .sqz file and generates
report-ready content matching standard WQ Assessment formats.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from openmusic import SQZExtractor, MusicFileParser, ReportGenerator


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate report sections from MUSIC .sqz files'
    )
    parser.add_argument(
        'input',
        help='Input .sqz file'
    )
    parser.add_argument(
        '-o', '--output',
        default='d:\\GitRepos\\OpenMUSIC\\data\\outputs\\report.md',
        help='Output report file path'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    logger = logging.getLogger(__name__)

    sqz_path = Path(args.input)
    if not sqz_path.exists():
        print(f"Error: File not found: {sqz_path}")
        return 1

    print(f"Generating report from: {sqz_path.name}")
    print("-" * 60)

    try:
        # Extract and parse
        with SQZExtractor() as extractor:
            music_file = extractor.extract(sqz_path)
            parser = MusicFileParser(music_file)
            model = parser.parse()

        # Generate report
        report_gen = ReportGenerator(model)
        sections = report_gen.generate_full_report()

        # Display sections (encode safely for Windows console)
        for section_name, content in sections.items():
            print(f"\n## {section_name.replace('_', ' ').title()}")
            # Encode to ASCII-safe for Windows console
            safe_content = content.encode('ascii', 'replace').decode('ascii')
            print(safe_content)
            print()

        # Save to file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report_gen.save_full_report(output_path)

        print("-" * 60)
        print(f"Full report saved to: {output_path}")

        return 0

    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
