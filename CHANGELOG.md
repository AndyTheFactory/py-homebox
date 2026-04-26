# v 0.4.0

Upgrade the client to Homebox API v0.24.0.

* aligned the client with v24 item/template response compatibility:
	* `GET /v1/items/{id}`
	* `PUT /v1/items/{id}`
	* `PATCH /v1/items/{id}`
	* `POST /v1/items/{id}/attachments`
	* `PUT /v1/items/{id}/attachments/{attachment_id}`
	* `POST /v1/items/{id}/duplicate`
	* `POST /v1/templates/{id}/create-item`
* added response unwrapping for wrapped payload shapes (`item` and `data`) on affected endpoints
* added non-JSON success response fallback in the HTTP request layer for improved compatibility
* kept backward compatibility for existing method signatures and return models
* expanded template-field typing support for v24 (`text`, `number`, `boolean`, `time`) via `TemplateFieldType`
* added compatibility tests for wrapped v24 response shapes and attachment update fallback behavior

# v 0.3.0

Upgrade the client to Homebox API v0.23.0.

* added support for new endpoints introduced in v23:
	* `POST /v1/actions/wipe-inventory`
	* `GET /v1/groups/all`
	* `POST /v1/groups`
	* `DELETE /v1/groups`
	* `GET /v1/groups/invitations`
	* `POST /v1/groups/invitations/{id}`
	* `DELETE /v1/groups/invitations/{id}`
	* `GET /v1/groups/members`
	* `POST /v1/groups/members`
	* `DELETE /v1/groups/members/{user_id}`
	* `GET /v1/groups/statistics/tags`
	* `GET /v1/tags`
	* `POST /v1/tags`
	* `GET /v1/tags/{id}`
	* `PUT /v1/tags/{id}`
	* `DELETE /v1/tags/{id}`
* migrated data structures from labels to tags to match v23:
	* `TagCreate`, `TagOut`, `TagSummary`
	* request fields now support `tagIds` in item and template DTOs
	* `GroupStatistics` now supports `totalTags`
	* `UserOut` now supports `defaultGroupId` and `groupIds`
	* added v23 DTOs: `CreateRequest`, `GroupMemberAdd`, `GroupAcceptInvitationResponse`, `WipeInventoryOptions`, `UserSummary`
* preserved backward compatibility for previously mapped label APIs:
	* `client.labels.*` remains available and transparently maps to `/v1/tags` endpoints
	* legacy model names (`LabelCreate`, `LabelOut`, `LabelSummary`, `TemplateLabelSummary`) remain importable as aliases
	* legacy fields (`labelIds`, `defaultLabelIds`, `labels`, `defaultLabels`, `totalLabels`) continue to work via compatibility mapping
* added new example scripts demonstrating usage of the new group and tag endpoints:
	* `examples/manage_groups.py`
	* `examples/manage_tags.py`

# v 0.2.0

Upgrade the client to Homebox API v0.22.0.

* added support for item template endpoints:
	* `GET /v1/templates`
	* `POST /v1/templates`
	* `GET /v1/templates/{id}`
	* `PUT /v1/templates/{id}`
	* `DELETE /v1/templates/{id}`
	* `POST /v1/templates/{id}/create-item`
* added support for OIDC authentication endpoints:
	* `GET /v1/users/login/oidc`
	* `GET /v1/users/login/oidc/callback`
* added new v22 data structures and fields:
	* `OIDCStatus` on `APISummary`
	* `oidcIssuer` and `oidcSubject` on `UserOut`
	* item-template request/response models
* validated that previously mapped endpoints remain compatible through the test suite
* added example script `examples/manage_templates.py` demonstrating usage of the new template endpoints

# v 0.1.0

Initial release of the Homebox API client library for Python.

* support for homebox v0.21.0 API
* basic authentication and API client functionality
* covers all API endpoints.

<!-- package description limit -->