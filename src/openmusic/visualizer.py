"""Visualization tools for MUSIC model topology.

Generates network diagrams and model structure visualizations.
"""

import logging
import re
from pathlib import Path
from typing import Union, Optional
from dataclasses import asdict

from .parser import MusicModel, MusicNode

logger = logging.getLogger(__name__)


def sanitize_string(text: str, max_length: int = 50) -> str:
    """Clean string for safe output by removing binary/control characters.

    Args:
        text: Input string potentially containing binary data.
        max_length: Maximum length for output.

    Returns:
        Sanitized string safe for output files.
    """
    if not text:
        return ""

    # Keep only printable ASCII characters
    printable = ''.join(c for c in text if 32 <= ord(c) <= 126)

    # Remove multiple spaces
    printable = re.sub(r'\s+', ' ', printable)

    # Trim and limit length
    return printable.strip()[:max_length]


class ModelVisualizer:
    """Create visual representations of MUSIC models."""

    def __init__(self, model: MusicModel):
        """Initialize with a parsed model.

        Args:
            model: The MusicModel to visualize.
        """
        self.model = model

    def to_graphviz(self, output_path: Optional[Union[str, Path]] = None) -> str:
        """Generate Graphviz DOT format representation.

        Args:
            output_path: Optional path to save DOT file.

        Returns:
            Graphviz DOT string.
        """
        lines = [
            'digraph MUSIC_Model {',
            '  rankdir=TB;',
            '  node [shape=box, style="rounded,filled", fontname="Arial"];',
            '  edge [fontname="Arial", fontsize=10];',
            '',
            f'  label="MUSIC Model: {len(self.model.nodes)} nodes";',
            '  labelloc="t";',
            '',
        ]

        # Color scheme by node type
        colors = {
            'ReceivingNode': '#8dc63f',      # WRM Green
            'UrbanSourceNode': '#00928f',    # WRM Teal
            'PondNode': '#1e4164',           # WRM Blue
            'WetlandNode': '#00539b',        # Bright Blue
            'BioRetentionNode': '#00b49d',   # Bright Teal
            'GrossPollutantTrapNode': '#485253',  # Charcoal
        }

        # Add nodes
        for i, node in enumerate(self.model.nodes):
            node_id = f"node_{i}"
            color = colors.get(node.node_type, '#d7df23')  # Default: Citrus

            # Clean name for label
            label = sanitize_string(node.name, 30) or node.node_type
            label = label.replace('"', '\\"')

            lines.append(
                f'  {node_id} [label="{label}\\n({node.node_type})", '
                f'fillcolor="{color}", fontcolor="white"];'
            )

        # Add edges (if we can determine connectivity)
        # For now, assume linear flow: sources -> treatment -> receiving
        source_nodes = [i for i, n in enumerate(self.model.nodes)
                        if 'Source' in n.node_type]
        treatment_nodes = [i for i, n in enumerate(self.model.nodes)
                           if n.node_type not in ['ReceivingNode', 'UrbanSourceNode']]
        receiving_nodes = [i for i, n in enumerate(self.model.nodes)
                           if n.node_type == 'ReceivingNode']

        # Connect sources to treatments or receiving
        for src_idx in source_nodes:
            if treatment_nodes:
                for treat_idx in treatment_nodes:
                    lines.append(f'  node_{src_idx} -> node_{treat_idx};')
            elif receiving_nodes:
                for recv_idx in receiving_nodes:
                    lines.append(f'  node_{src_idx} -> node_{recv_idx};')

        # Connect treatments to receiving
        for treat_idx in treatment_nodes:
            for recv_idx in receiving_nodes:
                lines.append(f'  node_{treat_idx} -> node_{recv_idx};')

        lines.append('}')

        dot_content = '\n'.join(lines)

        if output_path:
            output_path = Path(output_path)
            output_path.write_text(dot_content, encoding='utf-8')
            logger.info(f"Saved Graphviz DOT to: {output_path}")

        return dot_content

    def to_ascii_diagram(self) -> str:
        """Generate simple ASCII text diagram of model structure.

        Returns:
            ASCII diagram string.
        """
        lines = [
            "=" * 60,
            "MUSIC Model Topology",
            "=" * 60,
            "",
        ]

        # Group by type
        sources = [n for n in self.model.nodes if 'Source' in n.node_type]
        treatments = [n for n in self.model.nodes
                      if n.node_type not in ['ReceivingNode', 'UrbanSourceNode']]
        receiving = [n for n in self.model.nodes if n.node_type == 'ReceivingNode']

        # Sources
        if sources:
            lines.append("SOURCES:")
            for node in sources:
                name = sanitize_string(node.name, 40) or "(unnamed)"
                lines.append(f"  [+] {node.node_type}: {name}")
            lines.append("")

        # Treatments
        if treatments:
            lines.append("TREATMENT:")
            for node in treatments:
                name = sanitize_string(node.name, 40) or "(unnamed)"
                lines.append(f"  [#] {node.node_type}: {name}")
            lines.append("")

        # Receiving
        if receiving:
            lines.append("RECEIVING:")
            for node in receiving:
                name = sanitize_string(node.name, 40) or "(unnamed)"
                lines.append(f"  [O] {node.node_type}: {name}")
            lines.append("")

        # Flow diagram
        lines.extend([
            "FLOW:",
            "  " + " -> ".join([
                f"Sources({len(sources)})",
                f"Treatment({len(treatments)})",
                f"Receiving({len(receiving)})"
            ]),
            "",
            "=" * 60,
        ])

        return "\n".join(lines)

    def generate_summary(self) -> dict:
        """Generate numerical summary of model.

        Returns:
            Dictionary with model statistics.
        """
        summary = {
            'total_nodes': len(self.model.nodes),
            'by_type': {},
            'has_coordinates': sum(1 for n in self.model.nodes if n.x or n.y),
            'total_properties': sum(len(n.properties) for n in self.model.nodes),
        }

        for node in self.model.nodes:
            node_type = node.node_type
            summary['by_type'][node_type] = summary['by_type'].get(node_type, 0) + 1

        return summary


def visualize_model(model: MusicModel, output_base: Union[str, Path],
                     formats: list = None) -> dict:
    """Generate visualizations in multiple formats.

    Args:
        model: The MusicModel to visualize.
        output_base: Base path for output files (no extension).
        formats: List of formats ('dot', 'txt'). Default: both.

    Returns:
        Dictionary mapping format to output path.
    """
    if formats is None:
        formats = ['dot', 'txt']

    output_base = Path(output_base)
    visualizer = ModelVisualizer(model)
    results = {}

    try:
        if 'dot' in formats:
            dot_path = output_base.with_suffix('.dot')
            visualizer.to_graphviz(dot_path)
            results['dot'] = dot_path
    except Exception as e:
        logger.error(f"Failed to generate Graphviz: {e}")

    try:
        if 'txt' in formats:
            txt_path = output_base.with_suffix('.txt')
            ascii_diagram = visualizer.to_ascii_diagram()
            txt_path.write_text(ascii_diagram, encoding='utf-8')
            results['txt'] = txt_path
    except Exception as e:
        logger.error(f"Failed to generate ASCII diagram: {e}")

    return results
