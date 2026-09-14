"""Pydantic models for the unified Homebox v0.26 entity API."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .items import DuplicateOptions, ItemAttachment
from .tags import TagSummary
from .types import EntityFieldType, EntityPathType


class EntityTypeSummary(BaseModel):
    """Entity type metadata embedded in entity responses."""

    model_config = ConfigDict(populate_by_name=True)

    createdAt: Optional[str] = None
    defaultTemplate: Optional["EntityTemplateSummary"] = None
    defaultTemplateId: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    id: Optional[str] = None
    isLocation: Optional[bool] = None
    name: Optional[str] = None
    updatedAt: Optional[str] = None


class EntityTypeCreate(BaseModel):
    """Payload for creating an entity type."""

    model_config = ConfigDict(populate_by_name=True)

    defaultTemplateId: Optional[str] = None
    icon: Optional[str] = None
    isLocation: Optional[bool] = None
    name: Optional[str] = None


class EntityTypeUpdate(EntityTypeCreate):
    """Payload for updating an entity type."""

    id: Optional[str] = None


class EntityFieldData(BaseModel):
    """Custom field value attached to an entity."""

    model_config = ConfigDict(populate_by_name=True)

    booleanValue: Optional[bool] = None
    id: Optional[str] = None
    name: Optional[str] = None
    numberValue: Optional[int] = None
    textValue: Optional[str] = None
    type: Optional[EntityFieldType] = None


class EntityCreate(BaseModel):
    """Payload for creating an entity."""

    model_config = ConfigDict(populate_by_name=True)

    description: Optional[str] = Field(default=None, max_length=1000)
    entityTypeId: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    parentId: Optional[str] = None
    quantity: Optional[float] = None
    tagIds: Optional[list[str]] = None


class EntityPatch(BaseModel):
    """Payload for partially updating an entity."""

    model_config = ConfigDict(populate_by_name=True)

    entityTypeId: Optional[str] = None
    id: Optional[str] = None
    parentId: Optional[str] = None
    quantity: Optional[float] = None
    tagIds: Optional[list[str]] = None


class EntityUpdate(BaseModel):
    """Payload for fully updating an entity."""

    model_config = ConfigDict(populate_by_name=True)

    archived: Optional[bool] = None
    assetId: Optional[str] = None
    description: Optional[str] = Field(default=None, max_length=1000)
    entityTypeId: Optional[str] = None
    fields: Optional[list[EntityFieldData]] = None
    id: Optional[str] = None
    insured: Optional[bool] = None
    lifetimeWarranty: Optional[bool] = None
    manufacturer: Optional[str] = None
    modelNumber: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    notes: Optional[str] = None
    parentId: Optional[str] = None
    purchaseDate: Optional[str] = None
    purchaseFrom: Optional[str] = Field(default=None, max_length=255)
    purchasePrice: Optional[float] = None
    quantity: Optional[float] = None
    serialNumber: Optional[str] = None
    soldDate: Optional[str] = None
    soldNotes: Optional[str] = None
    soldPrice: Optional[float] = None
    soldTo: Optional[str] = Field(default=None, max_length=255)
    syncChildEntityLocations: Optional[bool] = None
    tagIds: Optional[list[str]] = None
    warrantyDetails: Optional[str] = None
    warrantyExpires: Optional[str] = None


class EntitySummary(BaseModel):
    """Lightweight entity representation used by lists and nested relations."""

    model_config = ConfigDict(populate_by_name=True)

    archived: Optional[bool] = None
    assetId: Optional[str] = None
    createdAt: Optional[str] = None
    description: Optional[str] = None
    entityType: Optional[EntityTypeSummary] = None
    id: Optional[str] = None
    imageId: Optional[str] = None
    insured: Optional[bool] = None
    itemCount: Optional[float] = None
    name: Optional[str] = None
    parent: Optional["EntitySummary"] = None
    purchasePrice: Optional[float] = None
    quantity: Optional[float] = None
    soldDate: Optional[str] = None
    tags: Optional[list[TagSummary]] = None
    thumbnailId: Optional[str] = None
    updatedAt: Optional[str] = None


class EntityOut(EntitySummary):
    """Full entity representation returned by detail and mutation endpoints."""

    attachments: Optional[list[ItemAttachment]] = None
    children: Optional[list[EntitySummary]] = None
    fields: Optional[list[EntityFieldData]] = None
    lifetimeWarranty: Optional[bool] = None
    manufacturer: Optional[str] = None
    modelNumber: Optional[str] = None
    notes: Optional[str] = None
    purchaseDate: Optional[str] = None
    purchaseFrom: Optional[str] = None
    serialNumber: Optional[str] = None
    soldNotes: Optional[str] = None
    soldPrice: Optional[float] = None
    soldTo: Optional[str] = None
    syncChildEntityLocations: Optional[bool] = None
    totalPrice: Optional[float] = None
    warrantyDetails: Optional[str] = None
    warrantyExpires: Optional[str] = None


class EntityListResult(BaseModel):
    """Paginated entity query result."""

    model_config = ConfigDict(populate_by_name=True)

    items: Optional[list[EntitySummary]] = None
    page: Optional[int] = None
    pageSize: Optional[int] = None
    total: Optional[int] = None
    totalPrice: Optional[float] = None


class EntityPath(BaseModel):
    """One node in an entity ancestry path."""

    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[EntityPathType] = None


class ExternalAttachmentRequest(BaseModel):
    """Reference to a document stored in an external system."""

    model_config = ConfigDict(populate_by_name=True)

    attachment_type: Optional[str] = None
    external_id: Optional[str] = None
    source_type: Optional[str] = None
    title: Optional[str] = None


class EntityTemplateSummary(BaseModel):
    """Minimal template metadata embedded in entity types."""

    model_config = ConfigDict(populate_by_name=True)

    createdAt: Optional[str] = None
    description: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    updatedAt: Optional[str] = None


EntityTypeSummary.model_rebuild()
EntitySummary.model_rebuild()

__all__ = [
    "DuplicateOptions",
    "EntityCreate",
    "EntityFieldData",
    "EntityListResult",
    "EntityOut",
    "EntityPatch",
    "EntityPath",
    "EntitySummary",
    "EntityTemplateSummary",
    "EntityTypeCreate",
    "EntityTypeSummary",
    "EntityTypeUpdate",
    "EntityUpdate",
    "ExternalAttachmentRequest",
]
