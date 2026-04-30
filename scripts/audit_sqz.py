#!/usr/bin/env python3
"""CLI tool to audit MUSIC .sqz files.

Extracts and exports model data for QA/QC review.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from openmusic import SQZExtractor, MusicFileParser
from openmusic.exporter import export_model, ModelExporter
from openmusic.visualizer import visualize_model


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def audit_file(sqz_path: Path, output_dir: Path, formats: list) -> bool:
    """Audit a single .sqz file.

    Args:
        sqz_path: Path to .sqz file.
        output_dir: Directory to save outputs.
        formats: List of export formats.

    Returns:
        True if successful.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Auditing: {sqz_path.name}")

    try:
        # Extract and parse
        with SQZExtractor() as extractor:
            music_file = extractor.extract(sqz_path)
            parser = MusicFileParser(music_file)
            model = parser.parse()

        # Generate base output path
        base_name = sqz_path.stem.replace(' ', '_')
        output_base = output_dir / base_name

        # Export to requested formats
        exported = export_model(model, output_base, formats)

        for fmt, path in exported.items():
            logger.info(f"  -> {fmt}: {path}")

        # Export time series to subdirectory
        ts_dir = output_dir / f"{base_name}_timeseries"
        exporter = ModelExporter(model)
        ts_paths = exporter.export_time_series_csv(ts_dir)
        if ts_paths:
            logger.info(f"  -> timeseries: {len(ts_paths)} files in {ts_dir}")

        # Generate visualizations
        viz_base = output_dir / f"{base_name}_topology"
        viz_exported = visualize_model(model, viz_base, ['dot', 'txt'])
        for fmt, path in viz_exported.items():
            logger.info(f"  -> viz/{fmt}: {path}")

        # Print summary
        exporter = ModelExporter(model)
        print(exporter.generate_report())

        return True

    except Exception as e:
        logger.error(f"Failed to audit {sqz_path.name}: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Audit MUSIC .sqz files - extract and export model data'
    )
    parser.add_argument(
        'input',
        nargs='+',
        help='Input .sqz file(s) or directory'
    )
    parser.add_argument(
        '-o', '--output',
        default='d:\\GitRepos\\OpenMUSIC\\data\\outputs',
        help='Output directory for exports'
    )
    parser.add_argument(
        '-f', '--formats',
        default='json,csv,excel',
        help='Comma-separated export formats (default: json,csv,excel)'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Recursively search directories'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    # Resolve output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse formats
    formats = [f.strip().lower() for f in args.formats.split(',')]

    # Collect input files
    sqz_files = []
    for input_path in args.input:
        path = Path(input_path)
        if path.is_dir():
            pattern = '**/*.sqz' if args.recursive else '*.sqz'
            sqz_files.extend(path.glob(pattern))
        elif path.suffix.lower() == '.sqz':
            sqz_files.append(path)

    if not sqz_files:
        print(f"No .sqz files found in: {args.input}")
        return 1

    print(f"Found {len(sqz_files)} .sqz file(s) to audit")
    print(f"Output directory: {output_dir}")
    print(f"Export formats: {', '.join(formats)}")
    print("-" * 60)

    # Process each file
    success_count = 0
    for sqz_file in sqz_files:
        if audit_file(sqz_file, output_dir, formats):
            success_count += 1
        print()

    # Summary
    print("=" * 60)
    print(f"Complete: {success_count}/{len(sqz_files)} files processed successfully")
    print(f"Outputs saved to: {output_dir}")

    return 0 if success_count == len(sqz_files) else 1


if __name__ == '__main__':
    sys.exit(main())
