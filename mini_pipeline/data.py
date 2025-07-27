import json
from pathlib import Path
from typing import List, Dict


def load_scenes(path: Path) -> List[Dict]:
    """Load scenes from a JSON file."""
    with path.open() as f:
        data = json.load(f)
    return data.get("scenes", [])
