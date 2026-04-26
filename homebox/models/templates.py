"""Pydantic models for Homebox item template resource DTOs."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .types import TemplateFieldType


class TemplateField(BaseModel):
    """Custom text field definition used by item templates."""

    model_config = ConfigDict(
        populate_by_name=True,
    )
    booleanValue: Optional[bool] = None
    id: Optional[str] = None
    name: Optional[str] = None
    numberValue: Optional[int] = None
    textValue: Optional[str] = None
    timeValue: Optional[str] = None
    type: Optional[TemplateFieldType] = None


class TemplateTagSummary(BaseModel):
    """Minimal tag representation embedded in item templates."""

    model_config = ConfigDict(
        populate_by_name=True,
    )
    id: Optional[str] = None
    name: Optional[str] = None


class TemplateLocationSummary(BaseModel):
    """Minimal location representation embedded in item templates."""

    model_config = ConfigDict(
        populate_by_name=True,
    )
    id: Optional[str] = None
    name: Optional[str] = None


class ItemTemplateSummary(BaseModel):
    """Lightweight item template representation used in list responses."""

    model_config = ConfigDict(
        populate_by_name=True,
    )
    createdAt: Optional[str] = None
    description: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    updatedAt: Optional[str] = None


class ItemTemplateCreate(BaseModel):
    """Request payload for creating an item template."""

    model_config = ConfigDict(
        populate_by_name=True,
    )
    defaultDescription: Optional[str] = Field(default=None, max_length=1000)
    defaultInsured: Optional[bool] = None
    defaultTagIds: Optional[List[str]] = None
    defaultLabelIds: Optional[List[str]] = None
    defaultLifetimeWarranty: Optional[bool] = None
    defaultLocationId: Optional[str] = None
    defaultManufacturer: Optional[str] = Field(default=None, max_length=255)
    defaultModelNumber: Optional[str] = Field(default=None, max_length=255)
    defaultName: Optional[str] = Field(default=None, max_length=255)
    defaultQuantity: Optional[int] = None
    defaultWarrantyDetails: Optional[str] = Field(default=None, max_length=1000)
    description: Optional[str] = Field(default=None, max_length=1000)
    fields: Optional[List[TemplateField]] = None
    includePurchaseFields: Optional[bool] = None
    includeSoldFields: Optional[bool] = None
    includeWarrantyFields: Optional[bool] = None
    name: str = Field(..., min_length=1, max_length=255)
    notes: Optional[str] = Field(default=None, max_length=1000)


class ItemTemplateUpdate(BaseModel):
    """Request payload for updating an item template."""

    model_config = ConfigDict(
        populate_by_name=True,
    )
    defaultDescription: Optional[str] = Field(default=None, max_length=1000)
    defaultInsured: Optional[bool] = None
    defaultTagIds: Optional[List[str]] = None
    defaultLabelIds: Optional[List[str]] = None
    defaultLifetimeWarranty: Optional[bool] = None
    defaultLocationId: Optional[str] = None
    defaultManufacturer: Optional[str] = Field(default=None, max_length=255)
    defaultModelNumber: Optional[str] = Field(default=None, max_length=255)
    defaultName: Optional[str] = Field(default=None, max_length=255)
    defaultQuantity: Optional[int] = None
    defaultWarrantyDetails: Optional[str] = Field(default=None, max_length=1000)
    description: Optional[str] = Field(default=None, max_length=1000)
    fields: Optional[List[TemplateField]] = None
    id: Optional[str] = None
    includePurchaseFields: Optional[bool] = None
    includeSoldFields: Optional[bool] = None
    includeWarrantyFields: Optional[bool] = None
    name: str = Field(..., min_length=1, max_length=255)
    notes: Optional[str] = Field(default=None, max_length=1000)


class ItemTemplateOut(BaseModel):
    """Full item template representation returned by template endpoints."""

    model_config = ConfigDict(
        populate_by_name=True,
    )
    createdAt: Optional[str] = None
    defaultDescription: Optional[str] = None
    defaultInsured: Optional[bool] = None
    defaultTags: Optional[List[TemplateTagSummary]] = None
    defaultLabels: Optional[List[TemplateTagSummary]] = None
    defaultLifetimeWarranty: Optional[bool] = None
    defaultLocation: Optional[TemplateLocationSummary] = None
    defaultManufacturer: Optional[str] = None
    defaultModelNumber: Optional[str] = None
    defaultName: Optional[str] = None
    defaultQuantity: Optional[int] = None
    defaultWarrantyDetails: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[List[TemplateField]] = None
    id: Optional[str] = None
    includePurchaseFields: Optional[bool] = None
    includeSoldFields: Optional[bool] = None
    includeWarrantyFields: Optional[bool] = None
    name: Optional[str] = None
    notes: Optional[str] = None
    updatedAt: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _sync_legacy_labels(cls, data):
        if isinstance(data, dict) and "defaultLabels" not in data and "defaultTags" in data:
            data["defaultLabels"] = data["defaultTags"]
        return data


class ItemTemplateCreateItemRequest(BaseModel):
    """Request payload for creating an item from a template."""

    model_config = ConfigDict(
        populate_by_name=True,
    )
    description: Optional[str] = Field(default=None, max_length=1000)
    tagIds: Optional[List[str]] = None
    labelIds: Optional[List[str]] = None
    locationId: str
    name: str = Field(..., min_length=1, max_length=255)
    quantity: Optional[int] = None


__all__ = [
    "ItemTemplateCreate",
    "ItemTemplateCreateItemRequest",
    "ItemTemplateOut",
    "ItemTemplateSummary",
    "ItemTemplateUpdate",
    "TemplateField",
    "TemplateTagSummary",
    "TemplateLocationSummary",
]

TemplateLabelSummary = TemplateTagSummary
