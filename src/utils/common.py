import json
import os
import yaml
from pathlib import Path
from typing import Any, Dict


def read_yaml(path: str) -> Dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def save_json(data: Any, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_json(path: str) -> Any:
    with open(path, "r") as f:
        return json.load(f)


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def create_directories(dir_path: str) -> None:
    """Alias for ensure_dir - creates directories recursively."""
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def save_object(path: str, obj: any) -> None:
    """Pickle and save object to disk."""
    import pickle
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def load_object(path: str) -> any:
    """Load pickled object from disk."""
    import pickle
    with open(path, "rb") as f:
        return pickle.load(f)