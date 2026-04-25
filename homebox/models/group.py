"""Pydantic models for Homebox group / internal graph entities."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .users import User


class Group(BaseModel):
    """Internal ORM entity representing a Homebox group."""

    model_config = ConfigDict(
        populate_by_name=True,
    )
    created_at: Optional[str] = Field(default=None, description='CreatedAt holds the value of the "created_at" field.')
    currency: Optional[str] = Field(default=None, description='Currency holds the value of the "currency" field.')
    edges: Optional[GroupEdges] = Field(
        default=None,
        description="Edges holds the relations/edges for other nodes in the graph.\nThe values are being populated by the GroupQuery when eager-loading is set.",
    )
    id: Optional[str] = Field(default=None, description="ID of the ent.")
    name: Optional[str] = Field(default=None, description='Name holds the value of the "name" field.')
    updated_at: Optional[str] = Field(default=None, description='UpdatedAt holds the value of the "updated_at" field.')


class GroupEdges(BaseModel):
    """Graph edges for the Group ORM entity."""

    model_config = ConfigDict(
        populate_by_name=True,
    )
    invitation_tokens: Optional[List[GroupInvitationToken]] = Field(
        default=None,
        description="InvitationTokens holds the value of the invitation_tokens edge.",
    )
    items: Optional[List["Item"]] = Field(default=None, description="Items holds the value of the items edge.")  # ty: ignore[unresolved-reference]
    labels: Optional[List["Label"]] = Field(default=None, description="Labels holds the value of the labels edge.")  # ty: ignore[unresolved-reference]
    locations: Optional[List["Location"]] = Field(  # ty: ignore[unresolved-reference]
        default=None, description="Locations holds the value of the locations edge."
    )
    notifiers: Optional[List["Notifier"]] = Field(  # ty: ignore[unresolved-reference]
        default=None, description="Notifiers holds the value of the notifiers edge."
    )
    users: Optional[List[User]] = Field(default=None, description="Users holds the value of the users edge.")


class GroupInvitationToken(BaseModel):
    """Internal ORM entity for a group invitation token."""

    model_config = ConfigDict(
        populate_by_name=True,
    )
    created_at: Optional[str] = Field(default=None, description='CreatedAt holds the value of the "created_at" field.')
    edges: Optional[GroupInvitationTokenEdges] = Field(
        default=None,
        description="Edges holds the relations/edges for other nodes in the graph.\nThe values are being populated by the GroupInvitationTokenQuery when eager-loading is set.",
    )
    expires_at: Optional[str] = Field(default=None, description='ExpiresAt holds the value of the "expires_at" field.')
    id: Optional[str] = Field(default=None, description="ID of the ent.")
    token: Optional[List[int]] = Field(default=None, description='Token holds the value of the "token" field.')
    updated_at: Optional[str] = Field(default=None, description='UpdatedAt holds the value of the "updated_at" field.')
    uses: Optional[int] = Field(default=None, description='Uses holds the value of the "uses" field.')


class GroupInvitationTokenEdges(BaseModel):
    """Graph edges for the GroupInvitationToken ORM entity."""

    model_config = ConfigDict(
        populate_by_name=True,
    )
    group: Optional[Group] = Field(default=None, description="Group holds the value of the group edge.")


class GroupStatistics(BaseModel):
    """Aggregate statistics for a group (items in group.py are the internal ORM entity).

    Note: This is the *internal* version used by the ORM entity. For the API DTO,
    see :class:`homebox.models.groups.GroupStatistics`.
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )
    totalItemPrice: Optional[float] = None
    totalItems: Optional[int] = None
    totalLabels: Optional[int] = None
    totalLocations: Optional[int] = None
    totalUsers: Optional[int] = None
    totalWithWarranty: Optional[int] = None


class GroupUpdate(BaseModel):
    """Payload for updating a group's name and/or currency (group.py internal)."""

    model_config = ConfigDict(
        populate_by_name=True,
    )
    currency: Optional[str] = None
    name: Optional[str] = None


class TotalsByOrganizer(BaseModel):
    """Aggregated total value for a single label or location organiser (group.py internal)."""

    model_config = ConfigDict(
        populate_by_name=True,
    )
    id: Optional[str] = None
    name: Optional[str] = None
    total: Optional[float] = None


class ValueOverTimeEntry(BaseModel):
    """A single data point in a time-series value report (group.py internal)."""

    model_config = ConfigDict(
        populate_by_name=True,
    )
    date: Optional[str] = None
    name: Optional[str] = None
    value: Optional[float] = None


class ValueOverTime(BaseModel):
    """Time-series purchase price report for a date range (group.py internal)."""

    model_config = ConfigDict(
        populate_by_name=True,
    )
    end: Optional[str] = None
    entries: Optional[List[ValueOverTimeEntry]] = None
    start: Optional[str] = None
    valueAtEnd: Optional[float] = None
    valueAtStart: Optional[float] = None


Group.model_rebuild(raise_errors=False)
GroupEdges.model_rebuild(raise_errors=False)
GroupInvitationToken.model_rebuild(raise_errors=False)
