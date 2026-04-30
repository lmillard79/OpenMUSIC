"""OpenMUSIC - MUSIC stormwater model file parser and auditor.

This package provides tools for reading, analyzing, and extracting data
from MUSIC .sqz model files without requiring the MUSIC software or dongle.
"""

__version__ = "0.1.0"
__author__ = "OpenMUSIC Project"

from .parser import MusicFileParser, MusicModel, MusicNode, TimeSeries
from .extractor import SQZExtractor
from .exporter import ModelExporter, export_model
from .visualizer import ModelVisualizer, visualize_model
from .report_generator import ReportGenerator
from .topology_viz import build_ascii_topology, build_flow_table, save_topology
from .topology_extractor import build_directional_topology, build_connection_topology, save_topology_with_connections

__all__ = [
    "MusicFileParser",
    "MusicModel",
    "MusicNode",
    "TimeSeries",
    "SQZExtractor",
    "ModelExporter",
    "export_model",
    "ModelVisualizer",
    "visualize_model",
    "ReportGenerator",
    "build_ascii_topology",
    "build_flow_table",
    "save_topology",
    "build_directional_topology",
    "build_connection_topology",
    "save_topology_with_connections",
]
