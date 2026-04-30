"""ZIP extraction layer for .sqz files.

MUSIC .sqz files are ZIP archives containing a single 'MusicDataFile'.
This module handles the extraction process.
"""

import zipfile
import os
import tempfile
import shutil
from pathlib import Path
from typing import Union, Optional
import logging

logger = logging.getLogger(__name__)


class SQZExtractor:
    """Extracts MusicDataFile from MUSIC .sqz archives."""

    def __init__(self, cleanup: bool = True):
        """Initialize extractor.

        Args:
            cleanup: If True, remove temporary extraction directory on cleanup.
        """
        self._temp_dir: Optional[Path] = None
        self._cleanup = cleanup

    def extract(self, sqz_path: Union[str, Path]) -> Path:
        """Extract MusicDataFile from .sqz archive.

        Args:
            sqz_path: Path to the .sqz file.

        Returns:
            Path to the extracted MusicDataFile.

        Raises:
            FileNotFoundError: If sqz_path does not exist.
            zipfile.BadZipFile: If the file is not a valid ZIP archive.
            ValueError: If MusicDataFile is not found in archive.
        """
        sqz_path = Path(sqz_path)
        if not sqz_path.exists():
            raise FileNotFoundError(f"SQZ file not found: {sqz_path}")

        # Create temporary directory for extraction
        self._temp_dir = Path(tempfile.mkdtemp(prefix="openmusic_"))
        extract_dir = self._temp_dir / "extracted"
        extract_dir.mkdir()

        logger.info(f"Extracting {sqz_path} to {extract_dir}")

        # Extract ZIP contents
        try:
            with zipfile.ZipFile(sqz_path, 'r') as zf:
                zf.extractall(extract_dir)
        except zipfile.BadZipFile as e:
            self._cleanup_temp()
            raise zipfile.BadZipFile(f"Invalid SQZ file: {sqz_path}") from e

        # Locate MusicDataFile
        music_data_file = extract_dir / "MusicDataFile"
        if not music_data_file.exists():
            self._cleanup_temp()
            raise ValueError(f"MusicDataFile not found in archive: {sqz_path}")

        logger.info(f"Extracted MusicDataFile: {music_data_file} ({music_data_file.stat().st_size} bytes)")
        return music_data_file

    def _cleanup_temp(self) -> None:
        """Remove temporary extraction directory."""
        if self._temp_dir and self._temp_dir.exists() and self._cleanup:
            shutil.rmtree(self._temp_dir, ignore_errors=True)
            logger.debug(f"Cleaned up temporary directory: {self._temp_dir}")

    def __enter__(self) -> "SQZExtractor":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - cleanup temporary files."""
        self._cleanup_temp()
