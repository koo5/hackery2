"""schnabel — SDK for cooperating processes to share quadstore-shaped runtime state.

See ../docs/ for vision, prior art, decisions, current design, and roadmap.
"""

from .events import EventLog
from . import vocab

__all__ = ["EventLog", "vocab"]
