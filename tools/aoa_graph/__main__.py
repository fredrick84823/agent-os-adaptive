"""允許 `python3 tools/aoa_graph <repo>` 直接執行（不需安裝成套件）。"""
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aoa_graph.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
