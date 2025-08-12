from __future__ import annotations

import json
import os
import time
import re

from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import numpy as np
import yaml


def load_config(path: str = "config.yaml") -> Dict[str, Any]:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def read_json(path: str) -> Any:
    with open(path, "r") as f:
        return json.load(f)


def write_json(path: str, data: Any, indent: int = 2) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=indent)


def cosine_similarity_old(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def cosine_similarity(a: np.ndarray | list, b: np.ndarray | list) -> float:
    """
    Compute the cosine similarity of two embeddings.

    Parameters
    ----------
    a, b : np.ndarray | list
        1‑D embedding vectors.  If you receive a plain list, it will be
        automatically converted to an array before we do the math.

    Returns
    -------
    float
        Cosine similarity score in [-1, 1].
    """
    # Convert to a Numpy array (keeps dtype, no copying if already an array)
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    # Flatten – works even if `a`/`b` were 2‑D (e.g. (1, 1024))
    a = a.reshape(-1)
    b = b.reshape(-1)

    # dot product and norms
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    # Guard against a zero‑vector (division by 0)
    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot / (norm_a * norm_b))


def timer(func):
    """Decorator that adds 'elapsed_seconds' to the returned dict."""
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        if isinstance(result, dict):
            result["elapsed_seconds"] = elapsed
        else:
            result = {"result": result, "elapsed_seconds": elapsed}
        return result
    return wrapper


def token_count(text: str) -> int:
    char_count = len(text)
    estimated_tokens = char_count // 4
    return max(1, estimated_tokens)


def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            return json.dumps(data) # return json string
        except json.JSONDecodeError:
            print("Failed to parse JSON")
    return ""


# --------------------------------------------------------------- #
# Helper: Grab a client name from the LLM‑extracted entities
# --------------------------------------------------------------- #
def _extract_client_name(
    extracted: Dict[str, List[Dict[str, Any]]],
) -> str | None:
    """Return the first non‑empty ``client_name`` found in *extracted*."""

    if not extracted:
        return None

    for entities in extracted.values():
        if not hasattr(entities, "__iter__") or isinstance(entities, (str, bytes)):
            return None
        
        for entity in entities:
            name = entity.get("client_name") or entity.get("client_name", None)
            if name:
                return str(name).strip()
    return None


def get_client_name(
    extracted: Dict[str, List[Dict[str, Any]]],
) -> str:
    """
    Return a usable customer name for output files.

    Parameters
    ----------
    extracted :
        The dictionary returned by the LLM extraction stage.

    Returns
    -------
    str
        A string safe to use as a filename component, e.g.
        ``Acme_Corp`` or ``customerX``.
    """
    # 1️⃣ Try to pull a real name
    name = _extract_client_name(extracted)
    if name:
        # Sanitize for file names: keep letters, numbers, underscore, hyphen
        # Replace spaces with underscores
        safe_name = "".join(
            c if c.isalnum() or c in ("_", "-") else "_" for c in name.replace(" ", "")
        )
        return safe_name.strip("_")

    # 2️⃣ No real name – fall back to the literal string
    return "customerX"