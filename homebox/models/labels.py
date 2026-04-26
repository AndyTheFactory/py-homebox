"""Backward-compatible aliases for tag models.

Homebox v23 renamed labels to tags. This module intentionally keeps the old
``Label*`` names importable and points them to the equivalent ``Tag*`` models.
"""

from .tags import TagCreate as LabelCreate
from .tags import TagOut as LabelOut
from .tags import TagSummary as LabelSummary

__all__ = [
    "LabelCreate",
    "LabelOut",
    "LabelSummary",
]
