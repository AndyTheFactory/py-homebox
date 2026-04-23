from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from . import types


class AuthRoles(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    edges: Optional[AuthRolesEdges] = Field(
        default=None,
        description="Edges holds the relations/edges for other nodes in the graph.\nThe values are being populated by the AuthRolesQuery when eager-loading is set.",
    )
    id: Optional[int] = Field(default=None, description="ID of the ent.")
    role: Optional[types.AuthRole] = Field(
        default=None, description='Role holds the value of the "role" field.'
    )


class AuthRolesEdges(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    token: Optional[AuthTokens] = Field(
        default=None, description="Token holds the value of the token edge."
    )


class AuthTokens(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    created_at: Optional[str] = Field(
        default=None, description='CreatedAt holds the value of the "created_at" field.'
    )
    edges: Optional[AuthTokensEdges] = Field(
        default=None,
        description="Edges holds the relations/edges for other nodes in the graph.\nThe values are being populated by the AuthTokensQuery when eager-loading is set.",
    )
    expires_at: Optional[str] = Field(
        default=None, description='ExpiresAt holds the value of the "expires_at" field.'
    )
    id: Optional[str] = Field(default=None, description="ID of the ent.")
    token: Optional[List[int]] = Field(
        default=None, description='Token holds the value of the "token" field.'
    )
    updated_at: Optional[str] = Field(
        default=None, description='UpdatedAt holds the value of the "updated_at" field.'
    )


class AuthTokensEdges(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    roles: Optional[AuthRoles] = Field(
        default=None, description="Roles holds the value of the roles edge."
    )
    user: Optional[User] = Field(default=None, description="User holds the value of the user edge.")


AuthRoles.model_rebuild(raise_errors=False)
AuthRolesEdges.model_rebuild(raise_errors=False)
AuthTokens.model_rebuild(raise_errors=False)
AuthTokensEdges.model_rebuild(raise_errors=False)
