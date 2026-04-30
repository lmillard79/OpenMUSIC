"""ASCII topology visualization for MUSIC models."""

from typing import List, Dict, Tuple
from .parser import MusicModel, MusicNode
import re


def clean_node_name(name: str) -> str:
    """Clean binary artifacts from node names."""
    if not name:
        return "Unnamed"

    # Keep only printable ASCII first
    name = ''.join(c for c in name if 32 <= ord(c) <= 126)

    # Remove binary prefix patterns - common patterns seen in MUSIC files
    # Pattern: banSourceNodeh or similar with node type markers
    name = re.sub(r'^ban[^a-zA-Z]*', '', name)  # Remove ban + non-letters
    name = re.sub(r'^an[^a-zA-Z]*', '', name)   # Remove an + non-letters
    name = re.sub(r'^T[^a-z]*', '', name)      # Remove T + lowercase (type markers)
    name = re.sub(r'SourceNodeh', '', name)     # Remove SourceNodeh
    name = re.sub(r'SourceNode', '', name)      # Remove SourceNode
    name = re.sub(r'ReceivingNodeh?', '', name) # Remove ReceivingNode
    name = re.sub(r'PondNodeh?', '', name)       # Remove PondNode

    # Remove binary suffixes (anything starting with @ or control chars)
    name = re.split(r'[@!#$%^&*()\[\]{}":;\x00-\x1f]', name)[0]

    # Trim whitespace and common leftover chars
    name = name.strip('hban')
    name = name.strip()

    return name or "Unnamed"


def extract_catchment_id(name: str) -> str:
    """Extract catchment identifier (C1, C2, C3, etc.)."""
    name = name.upper()
    match = re.search(r'C(\d+)', name)
    if match:
        return f"C{match.group(1)}"
    return "Unknown"


def infer_treatment_type(node_name: str) -> str:
    """Infer if this source uses Swale or Mitre Drains based on name."""
    name_lower = node_name.lower()

    # Access tracks use Mitre Drains
    if any(x in name_lower for x in ['access', 'track', 'road']):
        return "Mitre Drains"

    # Everything else uses Swale
    return "Swale"


def build_ascii_topology(model: MusicModel) -> str:
    """Build ASCII diagram of model topology.

    Flow: Source -> Buffer -> Treatment -> Pond -> Junction -> Receiving
    """
    lines = []

    # Group by catchment
    by_catchment: Dict[str, List[MusicNode]] = {}
    for node in model.nodes:
        if 'Source' in node.node_type:
            catch_id = extract_catchment_id(node.name)
            if catch_id not in by_catchment:
                by_catchment[catch_id] = []
            by_catchment[catch_id].append(node)

    # Find junction nodes
    junctions = [n for n in model.nodes if 'Junction' in n.node_type]
    receiving = [n for n in model.nodes if n.node_type == 'ReceivingNode']

    # Header
    lines.append("=" * 70)
    lines.append("MUSIC Model Topology")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Total Nodes: {len(model.nodes)}")
    lines.append(f"Catchments: {', '.join(sorted(by_catchment.keys()))}")
    lines.append("")

    # For each catchment
    for catch_id in sorted(by_catchment.keys()):
        sources = by_catchment[catch_id]

        lines.append(f"\n{'-' * 70}")
        lines.append(f"Catchment {catch_id} ({len(sources)} sources)")
        lines.append(f"{'-' * 70}")

        for src in sources:
            src_name = clean_node_name(src.name)
            area = src.properties.get('area_ha')
            area_str = f" ({area:.2f} ha)" if area else ""

            # Determine treatment type
            treatment = infer_treatment_type(src.name)

            # Build flow path
            lines.append(f"\n  {src_name}{area_str}")
            lines.append(f"       |")
            lines.append(f"       v")
            lines.append(f"    [Buffer]")
            lines.append(f"       |")
            lines.append(f"       v")
            lines.append(f"    [{treatment}]")
            lines.append(f"       |")
            lines.append(f"       v")
            lines.append(f"    [Pond]")
            lines.append(f"       |")
            lines.append(f"       v")

        # Junction for this catchment
        lines.append(f"  [{catch_id} Post-development Junction]")

    # Overall receiving
    if receiving:
        recv_name = clean_node_name(receiving[0].name)
        lines.append(f"\n       |")
        lines.append(f"       v")
        lines.append(f"    [Post-Development Node]")
        lines.append(f"       |")
        lines.append(f"       v")
        lines.append(f"    [Receiving: {recv_name}]")

    # Legend
    lines.append("\n" + "=" * 70)
    lines.append("Legend:")
    lines.append("  |  = Flow direction (down)")
    lines.append("  v  = Flow direction (arrow)")
    lines.append("  [] = Node type")
    lines.append("=" * 70)

    return "\n".join(lines)


def build_flow_table(model: MusicModel) -> str:
    """Build a text table showing flow paths."""
    lines = []

    lines.append("\nFlow Path Summary")
    lines.append("=" * 70)
    lines.append(f"{'Source':<40} {'Treatment':<15} {'Catchment':<10}")
    lines.append("-" * 70)

    for node in model.nodes:
        if 'Source' in node.node_type:
            name = clean_node_name(node.name)
            treatment = infer_treatment_type(node.name)
            catch = extract_catchment_id(node.name)
            area = node.properties.get('area_ha', 0)

            # Truncate long names
            display_name = name[:38] if len(name) <= 40 else name[:37] + "..."

            lines.append(f"{display_name:<40} {treatment:<15} {catch:<10}")

    lines.append("=" * 70)

    return "\n".join(lines)


def save_topology(model: MusicModel, output_path: str) -> None:
    """Save topology visualization to file."""
    ascii_diag = build_ascii_topology(model)
    flow_table = build_flow_table(model)

    content = f"""{ascii_diag}

{flow_table}
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
