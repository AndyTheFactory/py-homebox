"""Public models API for Homebox.

This module re-exports the most commonly used schemas so consumers can keep
importing from ``homebox.models`` as they did before the refactor.
"""

from __future__ import annotations

from .currencies import Currency
from .groups import Group, GroupStatistics, GroupUpdate, TotalsByOrganizer, ValueOverTime, ValueOverTimeEntry
from .items import (
    DuplicateOptions,
    ItemAttachment,
    ItemAttachmentUpdate,
    ItemCreate,
    ItemFieldUpdate,
    ItemOut,
    ItemPatch,
    ItemPath,
    ItemSummary,
    ItemUpdate,
    PaginationResultRepoItemSummary,
)
from .labels import LabelCreate, LabelOut, LabelSummary
from .locations import LocationCreate, LocationOut, LocationOutCount, LocationSummary, LocationUpdate, TreeItem
from .maintenance import MaintenanceEntry, MaintenanceEntryCreate, MaintenanceEntryUpdate, MaintenanceEntryWithDetails
from .notifiers import NotifierCreate, NotifierOut, NotifierUpdate
from .products import BarcodeProduct
from .services import Latest, UserRegistration
from .tags import TagCreate, TagOut, TagSummary
from .templates import (
    ItemTemplateCreate,
    ItemTemplateCreateItemRequest,
    ItemTemplateOut,
    ItemTemplateSummary,
    ItemTemplateUpdate,
    TemplateField,
    TemplateLabelSummary,
    TemplateLocationSummary,
    TemplateTagSummary,
)
from .types import (
    AttachmentType,
    AuthRole,
    ItemFieldType,
    ItemType,
    MaintenanceFilterStatus,
    TemplateFieldType,
    UserRole,
)
from .users import UserOut, UserSummary, UserUpdate
from .v1 import (
    ActionAmountResult,
    APISummary,
    Build,
    ChangePassword,
    CreateRequest,
    GroupAcceptInvitationResponse,
    GroupInvitation,
    GroupInvitationCreate,
    GroupMemberAdd,
    ItemAttachmentToken,
    LoginForm,
    OIDCStatus,
    TokenResponse,
    WipeInventoryOptions,
    Wrapped,
)
from .validate import ErrorResponse

__all__ = [
    "APISummary",
    "ActionAmountResult",
    "AuthRole",
    "BarcodeProduct",
    "Build",
    "ChangePassword",
    "CreateRequest",
    "Currency",
    "DuplicateOptions",
    "ErrorResponse",
    "Group",
    "GroupInvitation",
    "GroupAcceptInvitationResponse",
    "GroupInvitationCreate",
    "GroupMemberAdd",
    "GroupStatistics",
    "GroupUpdate",
    "ItemAttachment",
    "ItemAttachmentToken",
    "ItemAttachmentUpdate",
    "ItemCreate",
    "ItemFieldUpdate",
    "ItemFieldType",
    "ItemOut",
    "ItemPatch",
    "ItemPath",
    "ItemSummary",
    "ItemTemplateCreate",
    "ItemTemplateCreateItemRequest",
    "ItemTemplateOut",
    "ItemTemplateSummary",
    "ItemTemplateUpdate",
    "ItemType",
    "AttachmentType",
    "ItemUpdate",
    "LabelCreate",
    "LabelOut",
    "LabelSummary",
    "TagCreate",
    "TagOut",
    "TagSummary",
    "Latest",
    "LocationCreate",
    "LocationOut",
    "LocationOutCount",
    "LocationSummary",
    "LocationUpdate",
    "LoginForm",
    "MaintenanceEntry",
    "MaintenanceEntryCreate",
    "MaintenanceEntryUpdate",
    "MaintenanceEntryWithDetails",
    "MaintenanceFilterStatus",
    "NotifierCreate",
    "NotifierOut",
    "NotifierUpdate",
    "OIDCStatus",
    "PaginationResultRepoItemSummary",
    "TemplateField",
    "TemplateLabelSummary",
    "TemplateTagSummary",
    "TemplateLocationSummary",
    "TemplateFieldType",
    "TokenResponse",
    "TotalsByOrganizer",
    "TreeItem",
    "UserOut",
    "UserSummary",
    "UserRegistration",
    "UserRole",
    "UserUpdate",
    "ValueOverTime",
    "ValueOverTimeEntry",
    "Wrapped",
    "WipeInventoryOptions",
]
