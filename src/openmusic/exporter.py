"""Export MUSIC model data to various formats.

Supports Excel, CSV, and JSON output for QA/QC workflows.
"""

import json
import csv
import re
from pathlib import Path
from typing import Union, List, Dict, Any
from dataclasses import asdict
import logging

from .parser import MusicModel, MusicNode


def sanitize_string(text: str, max_length: int = 100) -> str:
    """Clean string for safe output by removing binary/control characters."""
    if not text:
        return ""
    # Keep only printable ASCII characters
    printable = ''.join(c for c in text if 32 <= ord(c) <= 126)
    # Remove multiple spaces
    printable = re.sub(r'\s+', ' ', printable)
    return printable.strip()[:max_length]

logger = logging.getLogger(__name__)


class ModelExporter:
    """Export parsed MUSIC models to various formats."""

    def __init__(self, model: MusicModel):
        """Initialize with a parsed model.

        Args:
            model: The MusicModel to export.
        """
        self.model = model

    def to_json(self, output_path: Union[str, Path], indent: int = 2) -> Path:
        """Export model to JSON file.

        Args:
            output_path: Path to save JSON file.
            indent: JSON indentation level.

        Returns:
            Path to the saved file.
        """
        output_path = Path(output_path)

        data = {
            'version': self.model.version,
            'metadata': self.model.metadata,
            'node_count': len(self.model.nodes),
            'time_series_count': len(self.model.time_series),
            'nodes': [self._node_to_dict(n) for n in self.model.nodes],
            'time_series': [self._time_series_to_dict(ts) for ts in self.model.time_series],
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)

        logger.info(f"Exported JSON to: {output_path}")
        return output_path

    def to_csv(self, output_path: Union[str, Path]) -> Path:
        """Export node summary to CSV file.

        Args:
            output_path: Path to save CSV file.

        Returns:
            Path to the saved file.
        """
        output_path = Path(output_path)

        if not self.model.nodes:
            logger.warning("No nodes to export")
            return output_path

        # Flatten node data
        rows = []
        for node in self.model.nodes:
            row = {
                'node_type': node.node_type,
                'name': sanitize_string(node.name, 100),
                'node_id': node.node_id,
                'x': node.x,
                'y': node.y,
                'input_count': len(node.inputs),
                'output_count': len(node.outputs),
            }
            # Add key properties if present
            for key in ['area', 'area_ha', 'rainfall', 'runoff', 'treatment']:
                if key in node.properties:
                    row[key] = sanitize_string(str(node.properties[key]), 50)
            rows.append(row)

        # Write CSV
        if rows:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

        logger.info(f"Exported CSV to: {output_path}")
        return output_path

    def export_time_series_csv(self, output_dir: Union[str, Path]) -> List[Path]:
        """Export each time series to a separate CSV file.

        Args:
            output_dir: Directory to save CSV files.

        Returns:
            List of paths to saved files.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        saved_paths = []

        for i, ts in enumerate(self.model.time_series):
            # Create filename from series type and index
            safe_name = ts.name.replace(' ', '_').replace('/', '_')
            filename = f"{i:03d}_{safe_name}.csv"
            output_path = output_dir / filename

            # Write time series data
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['index', 'value'])
                for idx, val in enumerate(ts.values):
                    writer.writerow([idx, val])

            saved_paths.append(output_path)

        logger.info(f"Exported {len(saved_paths)} time series CSV files to: {output_dir}")
        return saved_paths

    def to_excel(self, output_path: Union[str, Path]) -> Path:
        """Export model to Excel workbook with multiple sheets.

        Args:
            output_path: Path to save Excel file.

        Returns:
            Path to the saved file.
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas required for Excel export. Install: pip install pandas openpyxl")

        output_path = Path(output_path)

        # Create node summary DataFrame
        node_data = []
        for node in self.model.nodes:
            node_data.append({
                'Type': node.node_type,
                'Name': sanitize_string(node.name, 100),
                'ID': node.node_id,
                'X': node.x,
                'Y': node.y,
                'Inputs': len(node.inputs),
                'Outputs': len(node.outputs),
            })

        # Node type summary
        type_summary = {}
        for node in self.model.nodes:
            type_summary[node.node_type] = type_summary.get(node.node_type, 0) + 1

        summary_data = [{'Node Type': k, 'Count': v} for k, v in sorted(type_summary.items())]

        # Write to Excel with multiple sheets
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary sheet
            if summary_data:
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

            # Nodes sheet
            if node_data:
                pd.DataFrame(node_data).to_excel(writer, sheet_name='Nodes', index=False)

            # Metadata sheet
            meta_data = [
                {'Property': 'Version', 'Value': self.model.version},
                {'Property': 'Total Nodes', 'Value': len(self.model.nodes)},
                {'Property': 'Time Series Count', 'Value': len(self.model.time_series)},
            ]
            for k, v in self.model.metadata.items():
                meta_data.append({'Property': k, 'Value': str(v)})
            pd.DataFrame(meta_data).to_excel(writer, sheet_name='Metadata', index=False)

            # Time series summary sheet
            if self.model.time_series:
                ts_data = []
                for ts in self.model.time_series:
                    ts_data.append({
                        'Name': ts.name,
                        'Type': ts.metadata.get('type', 'unknown'),
                        'Count': ts.count,
                        'Min': ts.min_value,
                        'Max': ts.max_value,
                        'Sum': ts.sum_value,
                        'Mean': ts.metadata.get('mean', 0),
                    })
                pd.DataFrame(ts_data).to_excel(writer, sheet_name='TimeSeries', index=False)

        logger.info(f"Exported Excel to: {output_path}")
        return output_path

    def generate_report(self) -> str:
        """Generate a text summary report.

        Returns:
            Formatted report string.
        """
        lines = [
            "=" * 60,
            "MUSIC Model Summary Report",
            "=" * 60,
            f"Version: {self.model.version}",
            f"Total Nodes: {len(self.model.nodes)}",
            f"Time Series: {len(self.model.time_series)}",
            "",
            "Node Type Summary:",
            "-" * 40,
        ]

        # Count by type
        type_counts: Dict[str, int] = {}
        for node in self.model.nodes:
            type_counts[node.node_type] = type_counts.get(node.node_type, 0) + 1

        for node_type, count in sorted(type_counts.items()):
            lines.append(f"  {node_type}: {count}")

        # Time series summary
        if self.model.time_series:
            lines.extend(["", "Time Series Summary:", "-" * 40])
            ts_by_type: Dict[str, int] = {}
            for ts in self.model.time_series:
                t = ts.metadata.get('type', 'unknown')
                ts_by_type[t] = ts_by_type.get(t, 0) + 1
            for ts_type, count in sorted(ts_by_type.items()):
                lines.append(f"  {ts_type}: {count}")

        # Node details
        lines.extend(["", "Node Details:", "-" * 40])
        for node in self.model.nodes:
            name = sanitize_string(node.name, 50) or "(unnamed)"
            lines.append(f"\n[{node.node_type}] {name}")
            if node.x or node.y:
                lines.append(f"  Position: ({node.x:.1f}, {node.y:.1f})")
            if node.properties:
                lines.append(f"  Properties: {len(node.properties)}")

        lines.extend(["", "=" * 60])
        return "\n".join(lines)

    def _node_to_dict(self, node: MusicNode) -> Dict[str, Any]:
        """Convert MusicNode to dictionary with sanitized strings."""
        return {
            'node_type': node.node_type,
            'node_id': node.node_id,
            'name': sanitize_string(node.name, 100),
            'x': node.x,
            'y': node.y,
            'properties': {
                sanitize_string(k, 50): sanitize_string(str(v), 100)
                for k, v in node.properties.items()
            },
            'inputs': node.inputs,
            'outputs': node.outputs,
        }

    def _time_series_to_dict(self, ts) -> Dict[str, Any]:
        """Convert TimeSeries to dictionary."""
        return {
            'name': ts.name,
            'position': ts.position,
            'count': ts.count,
            'type': ts.metadata.get('type', 'unknown'),
            'min': ts.min_value,
            'max': ts.max_value,
            'sum': ts.sum_value,
            'mean': ts.metadata.get('mean', 0),
            'values': ts.values,  # Include full values array
        }


def export_model(model: MusicModel, base_path: Union[str, Path], formats: List[str] = None) -> Dict[str, Path]:
    """Export model to multiple formats.

    Args:
        model: The MusicModel to export.
        base_path: Base output path (without extension).
        formats: List of formats to export ('json', 'csv', 'excel').
                 Default: all formats.

    Returns:
        Dictionary mapping format to output path.
    """
    if formats is None:
        formats = ['json', 'csv', 'excel']

    base_path = Path(base_path)
    exporter = ModelExporter(model)
    results = {}

    try:
        if 'json' in formats:
            results['json'] = exporter.to_json(base_path.with_suffix('.json'))
    except Exception as e:
        logger.error(f"Failed to export JSON: {e}")

    try:
        if 'csv' in formats:
            results['csv'] = exporter.to_csv(base_path.with_suffix('.csv'))
    except Exception as e:
        logger.error(f"Failed to export CSV: {e}")

    try:
        if 'excel' in formats:
            results['excel'] = exporter.to_excel(base_path.with_suffix('.xlsx'))
    except Exception as e:
        logger.error(f"Failed to export Excel: {e}")

    return results
