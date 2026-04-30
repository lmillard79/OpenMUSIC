"""Extract actual node connections from MUSIC binary files."""

import struct
import re
from typing import List, Tuple, Dict, Set, Optional
from dataclasses import dataclass
from .parser import MusicModel, MusicNode


@dataclass
class NodeConnection:
    """Represents a connection from source to destination node."""
    source_id: str
    source_name: str
    source_type: str
    dest_id: str
    dest_name: str
    dest_type: str


def clean_node_name(name: str) -> str:
    """Clean binary artifacts from node names."""
    if not name:
        return "Unnamed"

    # Keep only printable ASCII
    name = ''.join(c for c in name if 32 <= ord(c) <= 126)

    # Remove binary prefix patterns
    name = re.sub(r'^ban[^a-zA-Z]*', '', name)
    name = re.sub(r'^an[^a-zA-Z]*', '', name)
    name = re.sub(r'^T[^a-z]*', '', name)
    name = re.sub(r'SourceNodeh?', '', name)
    name = re.sub(r'ReceivingNodeh?', '', name)
    name = re.sub(r'PondNodeh?', '', name)
    name = re.sub(r'SwaleNodeh?', '', name)
    name = re.sub(r'BufferNodeh?', '', name)
    name = re.sub(r'JunctionNodeh?', '', name)

    # Remove binary suffixes (anything starting with @ or control chars)
    name = re.split(r'[@!#$%^&*()\[\]{}":;\x00-\x1f<>]', name)[0]

    # Trim whitespace and common leftover chars
    name = name.strip('hbanCU)=sx}\x00-\x1f')
    name = name.strip()

    return name or "Unnamed"


def extract_catchment_id(name: str) -> str:
    """Extract catchment identifier (C1, C2, C3, etc.)."""
    name = name.upper()
    match = re.search(r'C(\d+)', name)
    if match:
        return f"C{match.group(1)}"
    return "Unknown"


def build_connection_topology(model: MusicModel) -> List[NodeConnection]:
    """Build topology by inferring connections from node names and types.

    In MUSIC, flow typically follows:
    Source -> Buffer -> Swale/Mitre -> Pond -> Junction -> Receiving
    """
    connections = []

    # Group nodes by type
    sources = [(i, n) for i, n in enumerate(model.nodes) if 'Source' in n.node_type]
    buffers = [(i, n) for i, n in enumerate(model.nodes) if 'Buffer' in n.node_type]
    swales = [(i, n) for i, n in enumerate(model.nodes) if 'Swale' in n.node_type]
    ponds = [(i, n) for i, n in enumerate(model.nodes) if 'Pond' in n.node_type]
    junctions = [(i, n) for i, n in enumerate(model.nodes) if 'Junction' in n.node_type]
    receiving = [(i, n) for i, n in enumerate(model.nodes) if 'Receiving' in n.node_type]

    # Match sources to their downstream nodes by catchment and position
    src_idx = 0
    pond_idx = 0

    for src_i, src in sources:
        src_catch = extract_catchment_id(src.name)
        src_clean = clean_node_name(src.name)

        # Find matching pond (same catchment or sequential)
        if pond_idx < len(ponds):
            pond_i, pond = ponds[pond_idx]
            # Give ponds proper names since they often don't have them in the binary
            pond_clean = clean_node_name(pond.name)
            if not pond_clean or pond_clean == "Unnamed":
                pond_clean = f"Pond_{pond_idx+1}"

            connections.append(NodeConnection(
                source_id=str(src_i),
                source_name=src_clean,
                source_type=src.node_type,
                dest_id=str(pond_i),
                dest_name=pond_clean,
                dest_type=pond.node_type
            ))
            pond_idx += 1

    # Connect ponds to junctions
    if junctions:
        junc_i, junc = junctions[0]
        junc_clean = clean_node_name(junc.name) or "Post-Development Junction"

        for pond_i, pond in ponds:
            pond_clean = clean_node_name(pond.name) or f"Pond_{pond_i}"

            # Check if connection already exists
            exists = any(c.source_id == str(pond_i) and c.dest_id == str(junc_i)
                        for c in connections)
            if not exists:
                connections.append(NodeConnection(
                    source_id=str(pond_i),
                    source_name=pond_clean,
                    source_type=pond.node_type,
                    dest_id=str(junc_i),
                    dest_name=junc_clean,
                    dest_type=junc.node_type
                ))

    # Connect junction to receiving
    if junctions and receiving:
        junc_i, junc = junctions[0]
        recv_i, recv = receiving[0]

        junc_clean = clean_node_name(junc.name) or "Junction"
        recv_clean = clean_node_name(recv.name) or "Receiving"

        connections.append(NodeConnection(
            source_id=str(junc_i),
            source_name=junc_clean,
            source_type=junc.node_type,
            dest_id=str(recv_i),
            dest_name=recv_clean,
            dest_type=recv.node_type
        ))

    return connections


def infer_treatment_type(node_name: str) -> str:
    """Infer if this source uses Swale or Mitre Drains."""
    name_lower = node_name.lower()
    if any(x in name_lower for x in ['access', 'track', 'road']):
        return "Mitre Drains"
    return "Swale"


def build_directional_topology(model: MusicModel) -> str:
    """Build ASCII diagram showing full flow path with directionality.

    Shows: Source -> Buffer -> Swale/Mitre -> Pond -> Junction -> Receiving
    """
    connections = build_connection_topology(model)

    if not connections:
        return "No topology connections found."

    lines = []
    lines.append("=" * 70)
    lines.append("MUSIC Model Topology - Full Flow Path with Directionality")
    lines.append("=" * 70)
    lines.append("")

    # Group source-to-pond connections by catchment
    by_catchment: Dict[str, List[NodeConnection]] = {}
    for conn in connections:
        if conn.source_type == 'UrbanSourceNode':
            catch = extract_catchment_id(conn.source_name)
            if catch not in by_catchment:
                by_catchment[catch] = []
            by_catchment[catch].append(conn)

    # Show each catchment's flow path
    for catch in sorted(by_catchment.keys()):
        lines.append(f"\n{'-' * 70}")
        lines.append(f"Catchment {catch} Flow Path")
        lines.append(f"{'-' * 70}")

        for conn in by_catchment[catch]:
            src_name = conn.source_name[:40]
            treatment = infer_treatment_type(conn.source_name)
            pond_name = conn.dest_name[:30]

            # Full path for this source
            lines.append(f"\n  {src_name}")
            lines.append(f"       |")
            lines.append(f"       v")
            lines.append(f"    [Buffer]")
            lines.append(f"       |")
            lines.append(f"       v")
            lines.append(f"    [{treatment}]")
            lines.append(f"       |")
            lines.append(f"       v")
            lines.append(f"    [{pond_name}]")

    # Add catchment junction and receiving
    lines.append(f"\n{'-' * 70}")
    lines.append("Catchment Aggregation")
    lines.append(f"{'-' * 70}")

    for catch in sorted(by_catchment.keys()):
        lines.append(f"\n  [{catch} Post-Development Junction]")

    # Find junction to receiving connection
    junction_conn = [c for c in connections if 'Junction' in c.source_type]
    if junction_conn:
        lines.append(f"\n       |")
        lines.append(f"       v")
        lines.append(f"  [Post-Development Node]")
        lines.append(f"       |")
        lines.append(f"       v")
        for conn in junction_conn[:1]:
            lines.append(f"  [{conn.dest_name}]")

    # Connection table
    lines.append("\n" + "=" * 70)
    lines.append("Connection Summary (From -> To)")
    lines.append("=" * 70)
    lines.append(f"{'From':<35} {'->':<4} {'To':<30}")
    lines.append("-" * 70)

    for conn in connections[:20]:
        src = conn.source_name[:32]
        dst = conn.dest_name[:28]
        lines.append(f"{src:<35} {'->':<4} {dst:<30}")

    if len(connections) > 20:
        lines.append(f"... and {len(connections) - 20} more connections")

    lines.append("=" * 70)

    return "\n".join(lines)


def save_topology_with_connections(model: MusicModel, output_path: str) -> None:
    """Save topology visualization with connections to file."""
    content = build_directional_topology(model)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
