# tests/conftest.py
# Ensure repository root (containing pyproject.toml) is on sys.path so tests can import plugins package.
import sys
from pathlib import Path

def find_repo_root(start: Path) -> Path:
    p = start.resolve()
    for parent in [p] + list(p.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    # fallback to two levels up
    return p.parents[1] if len(p.parents) >= 2 else p

repo_root = find_repo_root(Path(__file__).parent)
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
