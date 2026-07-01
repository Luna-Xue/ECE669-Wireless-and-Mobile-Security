"""Make the repo root importable for the pytest suite (no src/ layout)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
