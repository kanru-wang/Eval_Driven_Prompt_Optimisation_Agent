"""Load local dummy samples without leaking labels into classification calls."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType


@dataclass(frozen=True)
class ComplaintSample:
    sample_number: int
    class_label: str
    complaint_text: str


def _load_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_samples(path: str | Path) -> list[ComplaintSample]:
    module = _load_module(Path(path))
    raw_samples = getattr(module, "COMPLAINT_SAMPLES")
    return [
        ComplaintSample(
            sample_number=int(item["sample_number"]),
            class_label=str(item["class_label"]),
            complaint_text=str(item["complaint_text"]),
        )
        for item in raw_samples
    ]
