"""Models for Homebox v0.26 collection export and import jobs."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict

from .types import ExportKind, ExportStatus


class ExportOut(BaseModel):
    """Tracked asynchronous collection export or import job."""

    model_config = ConfigDict(populate_by_name=True)

    artifactPath: Optional[str] = None
    createdAt: Optional[str] = None
    error: Optional[str] = None
    groupId: Optional[str] = None
    id: Optional[str] = None
    kind: Optional[ExportKind] = None
    progress: Optional[int] = None
    sizeBytes: Optional[int] = None
    status: Optional[ExportStatus] = None
    updatedAt: Optional[str] = None


class ExportResults(BaseModel):
    """Collection export listing response."""

    model_config = ConfigDict(populate_by_name=True)

    items: Optional[list[ExportOut]] = None


__all__ = ["ExportOut", "ExportResults"]
