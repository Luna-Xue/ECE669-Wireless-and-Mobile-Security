"""Build supervised (logs -> diagnosis) data for fine-tuning an explainer."""
from .dataset import build_dataset, build_example, to_target

__all__ = ["build_dataset", "build_example", "to_target"]
