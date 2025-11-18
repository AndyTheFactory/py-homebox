from __future__ import annotations

from enum import Enum


class AttachmentType(Enum):
    DefaultType = "attachment"
    TypePhoto = "photo"
    TypeManual = "manual"
    TypeWarranty = "warranty"
    TypeAttachment = "attachment"
    TypeReceipt = "receipt"
    TypeThumbnail = "thumbnail"


class AuthRole(Enum):
    DefaultRole = "user"
    RoleAdmin = "admin"
    RoleUser = "user"
    RoleAttachments = "attachments"


class ItemFieldType(Enum):
    TypeText = "text"
    TypeNumber = "number"
    TypeBoolean = "boolean"
    TypeTime = "time"


class ItemType(Enum):
    ItemTypeLocation = "location"
    ItemTypeItem = "item"


class MaintenanceFilterStatus(Enum):
    MaintenanceFilterStatusScheduled = "scheduled"
    MaintenanceFilterStatusCompleted = "completed"
    MaintenanceFilterStatusBoth = "both"


class UserRole(Enum):
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
