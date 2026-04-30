#!/usr/bin/env python3
"""Quick script to show directional topology with connections."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from openmusic import SQZExtractor, MusicFileParser, build_directional_topology


def main():
    sqz_path = Path('d:/GitRepos/OpenMUSIC/data/example/2066-02_28022025_BESS_EXG_and_DEV.sqz')

    with SQZExtractor() as extractor:
        music_file = extractor.extract(sqz_path)
        parser = MusicFileParser(music_file)
        model = parser.parse()

    print(build_directional_topology(model))


if __name__ == '__main__':
    main()
