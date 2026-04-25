"""Enumeration types used across Homebox resource models."""

from __future__ import annotations

from enum import Enum


class AttachmentType(Enum):
    """Enumeration of attachment categories recognised by Homebox."""

    DefaultType = "attachment"
    TypePhoto = "photo"
    TypeManual = "manual"
    TypeWarranty = "warranty"
    TypeAttachment = "attachment"
    TypeReceipt = "receipt"
    TypeThumbnail = "thumbnail"


class AuthRole(Enum):
    """Enumeration of authentication token roles."""

    DefaultRole = "user"
    RoleAdmin = "admin"
    RoleUser = "user"
    RoleAttachments = "attachments"


class ItemFieldType(Enum):
    """Enumeration of data types available for item custom fields."""

    TypeText = "text"
    TypeNumber = "number"
    TypeBoolean = "boolean"
    TypeTime = "time"


class ItemType(Enum):
    """Enumeration used to distinguish item-path node types."""

    ItemTypeLocation = "location"
    ItemTypeItem = "item"


class MaintenanceFilterStatus(Enum):
    """Enumeration of maintenance-log filter values."""

    MaintenanceFilterStatusScheduled = "scheduled"
    MaintenanceFilterStatusCompleted = "completed"
    MaintenanceFilterStatusBoth = "both"


class UserRole(Enum):
    """Enumeration of user role levels within a group."""

    DefaultRole = "user"
    RoleUser = "user"
    RoleOwner = "owner"


__all__ = [
    "AttachmentType",
    "AuthRole",
    "ItemFieldType",
    "ItemType",
    "MaintenanceFilterStatus",
    "UserRole",
]
