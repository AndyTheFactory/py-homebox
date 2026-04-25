# v 0.2.0

Upgrade the client to Homebox API v0.22.0 (`swagger_v22.json`).

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

# v 0.1.0

Initial release of the Homebox API client library for Python.

* support for homebox v0.21.0 API
* basic authentication and API client functionality
* covers all API endpoints.

<!-- package description limit -->