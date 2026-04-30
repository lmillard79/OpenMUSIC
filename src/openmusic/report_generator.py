"""Generate structured report sections from MUSIC .sqz files.

This module creates report-ready content for Water Quality Assessment
documentation, matching the structure of typical Section 6 type reports.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .parser import MusicModel, MusicNode, TimeSeries
from .topology_extractor import build_directional_topology

logger = logging.getLogger(__name__)


def sanitize_string(text: str, max_length: int = 100) -> str:
    """Clean string for safe output."""
    if not text:
        return ""
    printable = ''.join(c for c in text if 32 <= ord(c) <= 126)
    printable = re.sub(r'\s+', ' ', printable)
    return printable.strip()[:max_length]


class ReportGenerator:
    """Generate structured report content from MUSIC models."""

    def __init__(self, model: MusicModel):
        """Initialize with a parsed model."""
        self.model = model

    def generate_full_report(self) -> Dict[str, str]:
        """Generate all report sections.

        Returns:
            Dictionary of report sections.
        """
        return {
            'executive_summary': self.generate_executive_summary(),
            'table_6_7_source_params': self.generate_table_6_7_source_params(),
            'catchment_table': self.generate_section_6_catchment_table(),
            'treatment_trains': self.generate_treatment_train_table(),
            'table_6_9_pollutant_loads': self.generate_table_6_9_pollutant_loads(),
            'topology': self.generate_topology_description(),
            'inputs_summary': self.generate_inputs_summary(),
            'results_summary': self.generate_results_summary(),
        }

    def generate_executive_summary(self) -> str:
        """Generate executive summary for the model."""
        source_count = sum(1 for n in self.model.nodes if 'Source' in n.node_type)
        treatment_count = sum(1 for n in self.model.nodes
                              if n.node_type not in ['ReceivingNode', 'UrbanSourceNode'])
        ts_count = len(self.model.time_series)

        return f"""### Executive Summary

This water quality assessment utilises the MUSIC (Model for Urban Stormwater Improvement
Conceptualisation) modelling software to evaluate stormwater quality for the project area.
The model comprises {source_count} urban source catchments, {treatment_count} treatment nodes,
and {ts_count} time series data arrays representing rainfall, runoff, and pollutant loads.

**Model Configuration:**
- MUSIC Version: {self.model.version}
- Total Nodes: {len(self.model.nodes)}
- Time Series Data Points: {ts_count}

**Pollutants Assessed:**
- Total Nitrogen (TN)
- Total Phosphorus (TP)
- Total Suspended Solids (TSS)
- Gross Pollutants
"""

    def generate_section_6_catchment_table(self) -> str:
        """Generate Table 6.2 style catchment description table."""
        lines = [
            "### Table 6.2 Modelled Water Quality Catchment Description",
            "",
            "| Catchment | Total Area (ha) | Description |",
            "|-----------|-----------------|-------------|",
        ]

        # Group nodes by catchment
        catchments = self._group_nodes_by_catchment()

        for catch_id, nodes in sorted(catchments.items()):
            total_area = self._calculate_catchment_area(nodes)
            description = self._build_catchment_description(catch_id, nodes)

            lines.append(f"| {catch_id} | {total_area:.2f} | {description} |")

        return "\n".join(lines)

    def generate_treatment_train_table(self) -> str:
        """Generate treatment train specification table."""
        lines = [
            "### Treatment Train Specifications",
            "",
            "| Catchment/MUSIC Node | Treatment Train | Description/Parameters |",
            "|---------------------|-----------------|------------------------|",
        ]

        for node in self.model.nodes:
            if 'Source' not in node.node_type and node.node_type != 'ReceivingNode':
                node_name = sanitize_string(node.name, 30) or f"Node_{id(node)}"
                treatment_type = node.node_type.replace('Node', '').replace('T', '')
                param_desc = self._format_node_params(node)

                lines.append(f"| {node_name} | {treatment_type} | {param_desc} |")

        return "\n".join(lines)

    def generate_pollutant_loads_table(self) -> str:
        """Generate Table 6.9 style pollutant loads comparison."""
        pollutant_data = self._aggregate_pollutant_loads()

        if not pollutant_data:
            return "### Pollutant Loads\n\nNo pollutant load data available in model."

        lines = [
            "### Table 6.9 WQ Study Area Comparison: Mean Annual Pollutant Loads",
            "",
            "| Pollutant | Post-development (kg/year) | Notes |",
            "|-----------|--------------------------|-------|",
        ]

        for pollutant, data in sorted(pollutant_data.items()):
            total_load = data.get('total', 0)
            max_load = data.get('max', 0)
            lines.append(f"| {pollutant} | {total_load:,.2f} | Peak: {max_load:.2f} kg |")

        return "\n".join(lines)

    def generate_topology_description(self) -> str:
        """Generate text description of model topology with full flow paths.

        Shows directional connections: Source -> Buffer -> Swale/Mitre -> Pond -> Junction -> Receiving
        """
        return "### Model Topology\n\n" + build_directional_topology(self.model)

    def generate_simple_topology_list(self) -> str:
        """Generate simple list-based topology (fallback)."""
        sources = [n for n in self.model.nodes if 'Source' in n.node_type]
        treatments = [n for n in self.model.nodes
                      if n.node_type not in ['ReceivingNode', 'UrbanSourceNode']]
        receiving = [n for n in self.model.nodes if n.node_type == 'ReceivingNode']

        lines = [
            "### Model Topology (Simple List)",
            "",
            f"The MUSIC model consists of {len(self.model.nodes)} nodes arranged in the following configuration:",
            "",
            f"**Source Nodes ({len(sources)}):**",
        ]

        for node in sources:
            name = sanitize_string(node.name, 40) or "Unnamed"
            area = node.properties.get('area_ha') or node.properties.get('area')
            area_str = f"{area:.2f} ha" if area else "Unknown"
            lines.append(f"- {name} (Area: {area_str})")

        lines.extend([
            "",
            f"**Treatment Nodes ({len(treatments)}):**",
        ])

        for node in treatments:
            name = sanitize_string(node.name, 40) or node.node_type
            lines.append(f"- {name}")

        if receiving:
            lines.extend([
                "",
                "**Receiving Node:**",
                f"- {sanitize_string(receiving[0].name, 40) or 'Receiving Waters'}",
            ])

        lines.extend([
            "",
            "**Flow Path:** Source -> Buffer -> Treatment -> Receiving",
        ])

        return "\n".join(lines)

    def generate_inputs_summary(self) -> str:
        """Generate summary of model inputs."""
        lines = [
            "### Model Inputs",
            "",
            "**Meteorological Data:**",
        ]

        # Find rainfall time series
        rainfall_ts = [ts for ts in self.model.time_series
                       if ts.metadata.get('type') == 'rainfall']

        if rainfall_ts:
            lines.append(f"- Rainfall time series: {len(rainfall_ts)} records")
            for ts in rainfall_ts[:3]:  # Show first 3
                lines.append(f"  - {ts.name}: {ts.count} time steps, "
                           f"total {ts.sum_value:.1f} mm")

        lines.extend([
            "",
            "**Catchment Parameters:**",
        ])

        for node in self.model.nodes:
            if 'Source' in node.node_type:
                name = sanitize_string(node.name, 30) or "Unnamed"
                area = node.properties.get('area_ha') or node.properties.get('area')
                area_str = f"{area:.2f} ha" if area else "N/A"
                lines.append(f"- {name}: {area_str}")

        return "\n".join(lines)

    def generate_results_summary(self) -> str:
        """Generate summary of model results."""
        lines = [
            "### Model Results Summary",
            "",
            "**Time Series Extracted:**",
        ]

        by_type: Dict[str, int] = {}
        for ts in self.model.time_series:
            t = ts.metadata.get('type', 'unknown')
            by_type[t] = by_type.get(t, 0) + 1

        for ts_type, count in sorted(by_type.items()):
            lines.append(f"- {ts_type.capitalize()}: {count} series")

        # Aggregate statistics
        lines.extend([
            "",
            "**Pollutant Load Statistics:**",
        ])

        pollutant_ts = [ts for ts in self.model.time_series
                       if 'pollutant' in ts.metadata.get('type', '')
                       or any(p in ts.name.upper() for p in ['TN', 'TP', 'TSS'])]

        if pollutant_ts:
            total_pollutants = sum(ts.sum_value for ts in pollutant_ts)
            lines.append(f"- Total modelled pollutant load: {total_pollutants:,.2f} kg")
            lines.append(f"- Number of pollutant time series: {len(pollutant_ts)}")

        return "\n".join(lines)

    def generate_table_6_7_source_params(self) -> str:
        """Generate Table 6.7: MUSIC source node parameter for post-development.

        Format:
        | Catchment/MUSIC Node | Project Design Feature | Source Node Type |
          MUSIC Surface Type | Area (ha) | Effective Impervious Area | Rainfall Threshold (mm) |
        """
        lines = [
            "### Table 6.7 MUSIC source node parameter for post-development",
            "",
            "| Catchment/MUSIC Node | Project Design Feature | Source Node Type | "
            "MUSIC Surface Type | Area (ha) | Effective Impervious Area | Rainfall Threshold (mm) |",
            "|---|---|---|---|---|---|---|",
        ]

        # Get all source nodes sorted by catchment
        sources = [n for n in self.model.nodes if 'Source' in n.node_type]
        sources.sort(key=lambda n: self._extract_catchment_id(n.name))

        for node in sources:
            # Clean up the node name for display
            node_name = self._clean_node_name_for_table(node.name)
            catch_id = self._extract_catchment_id(node.name)
            display_name = f"{catch_id}-{node_name}"

            # Extract project design feature from name
            project_feature = self._extract_project_feature(node.name)

            # Source node type is always Urban in these models
            source_type = "Urban"

            # Surface type from name
            surface_type = self._extract_surface_type(node.name)

            # Area from properties
            area = node.properties.get('area_ha')
            area_str = f"{area:.2f}" if area else "N/A"

            # Impervious and rainfall threshold - would need to be extracted from binary
            # For now, infer from surface type
            impervious = self._infer_impervious(surface_type)
            rainfall_thresh = "1.5"  # Standard value

            lines.append(
                f"| {display_name} | {project_feature} | {source_type} | "
                f"{surface_type} | {area_str} | {impervious} | {rainfall_thresh} |"
            )

        return "\n".join(lines)

    def generate_table_6_9_pollutant_loads(self) -> str:
        """Generate Table 6.9: WQ Study Area Comparison: Mean Annual Pollutant Loads.

        Format:
        | Pollutant | Pre-development (kg/year) | Post-development (kg/year) |
          Difference | Load Reduction | Neutral or beneficial effect |
        """
        lines = [
            "### Table 6.9 WQ Study Area Comparison: Mean Annual Pollutant Loads",
            "",
            "| Pollutant | Pre-development (kg/year) | Post-development (kg/year) | "
            "Difference | Load Reduction | Neutral or beneficial effect |",
            "|---|---|---|---|---|---|",
        ]

        # Aggregate pollutant loads by type from time series
        pollutant_data = self._calculate_annual_pollutant_loads()

        # Define pollutant order
        pollutants = ['TSS', 'TP', 'TN', 'Gross Pollutants']

        for pollutant in pollutants:
            data = pollutant_data.get(pollutant, {})

            pre_dev = data.get('pre_dev', 0)
            post_dev = data.get('post_dev', 0)
            difference = post_dev - pre_dev

            # Calculate reduction %
            if pre_dev > 0:
                reduction_pct = ((pre_dev - post_dev) / pre_dev) * 100
                reduction_str = f"{reduction_pct:.0f}%"
            else:
                reduction_str = "-"

            # Determine if beneficial (NorBE: 10% reduction required)
            is_beneficial = reduction_pct >= 10 if pre_dev > 0 else False
            beneficial_str = "True" if is_beneficial else "False"

            lines.append(
                f"| {pollutant} | {pre_dev:,.0f} | {post_dev:,.0f} | "
                f"{difference:+,.0f} | {reduction_str} | {beneficial_str} |"
            )

        return "\n".join(lines)

    def _group_nodes_by_catchment(self) -> Dict[str, List[MusicNode]]:
        """Group source nodes by catchment identifier."""
        catchments: Dict[str, List[MusicNode]] = {}

        for node in self.model.nodes:
            if 'Source' in node.node_type:
                # Extract catchment ID from node name (e.g., "C1-", "Catchment 1")
                catch_id = self._extract_catchment_id(node.name)
                if catch_id not in catchments:
                    catchments[catch_id] = []
                catchments[catch_id].append(node)

        return catchments

    def _extract_catchment_id(self, name: str) -> str:
        """Extract catchment identifier from node name."""
        name = sanitize_string(name, 50)

        # Look for patterns like C1, C2, Catchment 1, etc.
        patterns = [
            r'C(\d+)',
            r'Catchment\s+(\d+)',
            r'Catchment-(\d+)',
            r'Catchment (\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                return f"C{match.group(1)}"

        return "Unknown"

    def _extract_land_use(self, name: str) -> str:
        """Extract land use type from node name."""
        name_lower = name.lower()

        land_uses = {
            'roof': 'Roof',
            'road': 'Road',
            'track': 'Access Track',
            'park': 'Park',
            'compound': 'Construction Compound',
            'laydown': 'Laydown Area',
            'substation': 'Substation',
            'bess': 'BESS',
            'admin': 'Administration',
            'revegetated': 'Revegetated',
        }

        for key, value in land_uses.items():
            if key in name_lower:
                return value

        return "Urban"

    def _calculate_catchment_area(self, nodes: List[MusicNode]) -> float:
        """Calculate total area for a group of nodes."""
        total = 0.0
        for node in nodes:
            # Check properties for area_ha first (what parser now extracts)
            area = node.properties.get('area_ha')
            if area is None:
                area = node.properties.get('area')
            if area is None:
                area = node.properties.get('Area')

            if area is not None:
                try:
                    total += float(area)
                except (ValueError, TypeError):
                    pass
        return total

    def _build_catchment_description(self, catch_id: str, nodes: List[MusicNode]) -> str:
        """Build description text for a catchment."""
        land_uses = []
        for node in nodes:
            lu = self._extract_land_use(node.name)
            if lu not in land_uses:
                land_uses.append(lu)

        if land_uses:
            uses_text = ", ".join(land_uses)
            return f"{catch_id} consists of {uses_text}"
        return f"{catch_id} - No land use data"

    def _format_node_params(self, node: MusicNode) -> str:
        """Format node parameters for display."""
        params = []

        if node.properties:
            for key, value in list(node.properties.items())[:3]:
                clean_key = sanitize_string(key, 20)
                clean_val = sanitize_string(str(value), 20)
                params.append(f"{clean_key}: {clean_val}")

        return "; ".join(params) if params else "Standard configuration"

    def _aggregate_pollutant_loads(self) -> Dict[str, Dict[str, float]]:
        """Aggregate pollutant loads from time series."""
        pollutants: Dict[str, Dict[str, float]] = {}

        # Map time series to pollutant types
        for ts in self.model.time_series:
            ts_name = ts.name.upper()

            # Determine pollutant type
            pollutant_type = None
            if 'TN' in ts_name or 'NITROGEN' in ts_name:
                pollutant_type = 'TN'
            elif 'TP' in ts_name or 'PHOSPHORUS' in ts_name:
                pollutant_type = 'TP'
            elif 'TSS' in ts_name or 'SOLIDS' in ts_name:
                pollutant_type = 'TSS'
            elif 'GROSS' in ts_name or 'GP' in ts_name:
                pollutant_type = 'Gross Pollutants'

            if pollutant_type:
                if pollutant_type not in pollutants:
                    pollutants[pollutant_type] = {'total': 0, 'max': 0, 'count': 0}

                pollutants[pollutant_type]['total'] += ts.sum_value
                pollutants[pollutant_type]['max'] = max(
                    pollutants[pollutant_type]['max'], ts.max_value
                )
                pollutants[pollutant_type]['count'] += 1

        return pollutants

    def _clean_node_name_for_table(self, name: str) -> str:
        """Clean node name for table display."""
        # Remove binary artifacts
        name = sanitize_string(name, 50)

        # Remove common prefixes
        name = re.sub(r'^banSourceNodeh', '', name)
        name = re.sub(r'^anSourceNodeh', '', name)
        name = re.sub(r'^[hC]\d+-', '', name)  # Remove C2-, C3- prefix

        # Remove binary suffixes
        name = re.split(r'[@!#$%\x00-\x1f]', name)[0]
        name = name.strip('hbanCU')

        return name.strip() or "Unnamed"

    def _extract_project_feature(self, name: str) -> str:
        """Extract project design feature from node name."""
        name_lower = name.lower()

        features = [
            ('construction compound', '1 x Construction Compound'),
            ('o&m facility', 'O&M Facility'),
            ('o & m facility', 'O&M Facility'),
            ('substation', 'Substation'),
            ('bess', 'BESS'),
            ('laydown', '2 x Laydown Areas'),
            ('test bed', 'Test Bed'),
            ('administration', 'Administration Area'),
            ('admin area', 'Administration Area'),
            ('existing access track', 'Existing Access Track'),
            ('developed access track', 'New Access Track'),
            ('new access track', 'New Access Track'),
            ('access track', 'Access Track'),
        ]

        for key, value in features:
            if key in name_lower:
                return value

        return "Unknown"

    def _extract_surface_type(self, name: str) -> str:
        """Extract MUSIC surface type from node name."""
        name_lower = name.lower()

        # Unsealed road types
        if any(x in name_lower for x in ['access', 'track', 'road', 'unsealed']):
            return "Unsealed road"

        # Industrial areas
        if any(x in name_lower for x in ['compound', 'laydown', 'substation', 'bess', 'facility', 'admin', 'industrial']):
            return "Industrial"

        return "Industrial"  # Default

    def _infer_impervious(self, surface_type: str) -> str:
        """Infer impervious percentage from surface type."""
        impervious = {
            'Industrial': "25%",
            'Unsealed road': "35%",
        }
        return impervious.get(surface_type, "25%")

    def _calculate_annual_pollutant_loads(self) -> Dict[str, Dict[str, float]]:
        """Calculate annual pollutant loads from time series.

        Returns dict with pollutant type -> {pre_dev, post_dev}
        """
        # Initialize with zeros
        results = {
            'TSS': {'pre_dev': 0, 'post_dev': 0},
            'TP': {'pre_dev': 0, 'post_dev': 0},
            'TN': {'pre_dev': 0, 'post_dev': 0},
            'Gross Pollutants': {'pre_dev': 0, 'post_dev': 0},
        }

        # For now, use time series data as post-development
        # Pre-development would need separate extraction or model configuration
        for ts in self.model.time_series:
            ts_name = ts.name.upper()

            # Determine pollutant type
            pollutant_type = None
            if 'TN' in ts_name or 'NITROGEN' in ts_name:
                pollutant_type = 'TN'
            elif 'TP' in ts_name or 'PHOSPHORUS' in ts_name:
                pollutant_type = 'TP'
            elif 'TSS' in ts_name or 'SOLIDS' in ts_name or 'SUSPENDED' in ts_name:
                pollutant_type = 'TSS'
            elif 'GROSS' in ts_name or 'GP' in ts_name:
                pollutant_type = 'Gross Pollutants'

            if pollutant_type and pollutant_type in results:
                # Sum values as proxy for annual load
                # Note: Actual calculation needs time step conversion
                annual_load = ts.sum_value
                results[pollutant_type]['post_dev'] += annual_load

        return results

    def save_full_report(self, output_path: Path) -> None:
        """Save complete report to file."""
        sections = self.generate_full_report()

        lines = [
            "# MUSIC Model Report",
            f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Model Version: {self.model.version}",
            "",
            "---",
            "",
        ]

        for section_name, content in sections.items():
            lines.extend([
                content,
                "",
                "---",
                "",
            ])

        output_path.write_text("\n".join(lines), encoding='utf-8')
        logger.info(f"Saved full report to: {output_path}")
