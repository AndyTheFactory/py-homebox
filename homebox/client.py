"""Client classes for interacting with the Homebox REST API."""

from __future__ import annotations

import os
from typing import Any, Literal, Optional, overload

import requests

from homebox.models import (
    ActionAmountResult,
    APISummary,
    BarcodeProduct,
    ChangePassword,
    Currency,
    DuplicateOptions,
    Group,
    GroupInvitation,
    GroupInvitationCreate,
    GroupStatistics,
    GroupUpdate,
    ItemAttachmentUpdate,
    ItemCreate,
    ItemOut,
    ItemPatch,
    ItemPath,
    ItemSummary,
    ItemTemplateCreate,
    ItemTemplateCreateItemRequest,
    ItemTemplateOut,
    ItemTemplateSummary,
    ItemTemplateUpdate,
    ItemUpdate,
    LabelCreate,
    LabelOut,
    LabelSummary,
    LocationCreate,
    LocationOut,
    LocationOutCount,
    LocationSummary,
    LocationUpdate,
    LoginForm,
    MaintenanceEntry,
    MaintenanceEntryCreate,
    MaintenanceEntryUpdate,
    MaintenanceEntryWithDetails,
    MaintenanceFilterStatus,
    NotifierCreate,
    NotifierOut,
    NotifierUpdate,
    PaginationResultRepoItemSummary,
    TokenResponse,
    TotalsByOrganizer,
    TreeItem,
    UserOut,
    UserRegistration,
    UserUpdate,
    ValueOverTime,
)


class HomeboxClient:
    """Top-level client for the Homebox REST API.

    Provides direct access to authentication and top-level endpoints, and
    exposes namespaced sub-clients for every resource group (items, labels,
    locations, etc.).

    Attributes:
        base_url: Base URL of the Homebox API (e.g. ``https://demo.homebox.software/api``).
        token: Bearer token used to authenticate requests, or ``None`` when not
            yet authenticated.
        headers: HTTP headers sent with every request.
        actions: Sub-client for bulk action endpoints.
        assets: Sub-client for asset-ID lookup endpoints.
        groups: Sub-client for group and statistics endpoints.
        items: Sub-client for item CRUD and attachment endpoints.
        labels: Sub-client for label endpoints.
        locations: Sub-client for location endpoints.
        maintenance: Sub-client for maintenance-log endpoints.
        notifiers: Sub-client for notification-channel endpoints.
        users: Sub-client for user account endpoints.
        reporting: Sub-client for reporting / export endpoints.
        labelmaker: Sub-client for printable label endpoints.
        products: Sub-client for barcode/QR-code product endpoints.
        templates: Sub-client for item template endpoints.

    Example:
        >>> from homebox import HomeboxClient
        >>> client = HomeboxClient(base_url="https://demo.homebox.software/api")
        >>> client.login("admin@admin.com", "admin")
        >>> items = client.items.query_all_items()
    """

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        """Initialise the client.

        Args:
            base_url: Base URL of the Homebox API.  Falls back to the
                ``HOMEBOX_URL`` environment variable when not supplied.
            token: Pre-obtained Bearer token.  Falls back to the
                ``HOMEBOX_TOKEN`` environment variable when not supplied.  You
                can omit this and call :meth:`login` instead.

        Raises:
            ValueError: If ``base_url`` is not provided and ``HOMEBOX_URL`` is
                not set.
        """
        base_url = base_url or os.environ.get("HOMEBOX_URL")
        if not base_url:
            raise ValueError("base_url must be provided or the HOMEBOX_URL environment variable must be set")
        token = token or os.environ.get("HOMEBOX_TOKEN")
        self.base_url = base_url
        self.token = token
        self.headers = {"Content-Type": "application/json"}
        if token:
            self.headers["Authorization"] = f"{token}" if token.startswith("Bearer ") else f"Bearer {token}"

        self.actions = ActionsClient(self)
        self.assets = AssetsClient(self)
        self.groups = GroupsClient(self)
        self.items = ItemsClient(self)
        self.labels = LabelsClient(self)
        self.locations = LocationsClient(self)
        self.maintenance = MaintenanceClient(self)
        self.notifiers = NotifiersClient(self)
        self.users = UsersClient(self)
        self.reporting = ReportingClient(self)
        self.labelmaker = LabelMakerClient(self)
        self.products = ProductsClient(self)
        self.templates = TemplatesClient(self)

    def _request(self, method, endpoint, params=None, data=None, files=None, timeout=None) -> dict[Any, Any]:
        """Send an HTTP request and return the parsed JSON response body.

        Args:
            method: HTTP method string (e.g. ``"get"``, ``"post"``).
            endpoint: API path relative to :attr:`base_url` (e.g. ``"/v1/items"``).
            params: Optional query-string parameters.
            data: Optional request body, serialised as JSON.
            files: Optional multipart files mapping.
            timeout: Optional request timeout in seconds.

        Returns:
            Parsed JSON response as a dictionary.  List responses are wrapped
            under the ``"data"`` key.  HTTP 204 responses return an empty dict.

        Raises:
            requests.HTTPError: If the server returns a 4xx or 5xx status code.
        """
        headers = self.headers.copy()
        request_kwargs = {
            "params": params,
            "headers": headers,
            "timeout": timeout,
        }
        if files:
            del headers["Content-Type"]
            request_kwargs["data"] = data
            request_kwargs["files"] = files
        else:
            request_kwargs["json"] = data

        response = requests.request(
            method,
            f"{self.base_url}{endpoint}",
            **request_kwargs,
        )
        response.raise_for_status()

        if response.status_code == 204:
            return {}

        result = response.json()
        if isinstance(result, list):
            return {"data": result}
        return result

    @overload
    def _get(
        self, endpoint, params=None, data=None, files=None, timeout=None, binary: Literal[True] = True
    ) -> bytes: ...

    @overload
    def _get(
        self, endpoint, params=None, data=None, files=None, timeout=None, binary: Literal[False] = False
    ) -> str: ...

    def _get(self, endpoint, params=None, data=None, files=None, timeout=None, binary=False) -> str | bytes:
        """Send an HTTP GET request and return the raw response body.

        Used for endpoints that return non-JSON content (e.g. CSV exports,
        printable labels, and generated images).

        Args:
            endpoint: API path relative to :attr:`base_url`.
            params: Optional query-string parameters.
            data: Optional request body, serialised as JSON.
            files: Optional multipart files mapping.
            timeout: Optional request timeout in seconds.
            binary: When True return raw bytes, otherwise return decoded text.

        Returns:
            str | bytes: Raw response body (text by default, bytes when
            ``binary=True``). HTTP 204 responses return an empty string.

        Raises:
            requests.HTTPError: If the server returns a 4xx or 5xx status code.
        """
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()
        if files:
            del headers["Content-Type"]

        response = requests.get(url, params=params, json=data, files=files, headers=headers, timeout=timeout)
        response.raise_for_status()

        if response.status_code == 204:
            return ""

        return response.text if not binary else response.content

    def login(self, username, password, stay_logged_in=False, provider=None):
        """Authenticate with username and password and store the resulting token.

        After a successful login all subsequent requests made through this
        client automatically include the returned Bearer token.

        Args:
            username: Account e-mail address.
            password: Account password.
            stay_logged_in: When ``True`` the server issues a long-lived token.
                Defaults to ``False``.
            provider: Optional OAuth provider identifier.

        Returns:
            TokenResponse: Contains the ``token``, ``attachmentToken``, and
                ``expiresAt`` fields returned by the server.

        Raises:
            requests.HTTPError: If the credentials are rejected (HTTP 401) or
                any other server error occurs.
        """
        login_form = LoginForm(
            username=username,
            password=password,
            stayLoggedIn=stay_logged_in,
        )
        params = {}
        if provider:
            params["provider"] = provider

        response = self._request("post", "/v1/users/login", params=params, data=login_form.model_dump())
        token_response = TokenResponse(**response)
        self.token = token_response.token
        if self.token:
            self.headers["Authorization"] = (
                f"{self.token}" if self.token.startswith("Bearer ") else f"Bearer {self.token}"
            )
        return token_response

    def currency(self):
        """Return the group's configured currency.

        Returns:
            Currency: Currency metadata including code, name, symbol, and decimal
                precision.
        """
        return Currency(**self._request("get", "/v1/currency"))

    def application_info(self):
        """Return a summary of the running Homebox instance.

        Includes build information, feature flags (registration, demo mode, label
        printing), and the latest available release version.

        Returns:
            APISummary: Application status and build metadata.
        """
        return APISummary(**self._request("get", "/v1/status"))


class ActionsClient:
    """Sub-client for bulk action / maintenance endpoints.

    Accessed via ``HomeboxClient.actions``.
    """

    def __init__(self, client: HomeboxClient):
        self.client = client

    def create_missing_thumbnails(self) -> ActionAmountResult:
        """Create thumbnails for items that are missing them.

        Returns:
            ActionAmountResult: Number of thumbnails that were created.
        """
        return ActionAmountResult(**self.client._request("post", "/v1/actions/create-missing-thumbnails"))

    def ensure_asset_ids(self) -> ActionAmountResult:
        """Ensure all items in the database have an asset ID.

        Returns:
            ActionAmountResult: Number of asset IDs that were assigned.
        """
        return ActionAmountResult(**self.client._request("post", "/v1/actions/ensure-asset-ids"))

    def ensure_import_refs(self) -> ActionAmountResult:
        """Ensure all items in the database have an import reference.

        Returns:
            ActionAmountResult: Number of import refs that were assigned.
        """
        return ActionAmountResult(**self.client._request("post", "/v1/actions/ensure-import-refs"))

    def set_primary_photos(self) -> ActionAmountResult:
        """Set the first photo of each item as its primary photo.

        Returns:
            ActionAmountResult: Number of items whose primary photo was updated.
        """
        return ActionAmountResult(**self.client._request("post", "/v1/actions/set-primary-photos"))

    def zero_out_time_fields(self) -> ActionAmountResult:
        """Reset all item date fields to the beginning of the day.

        Returns:
            ActionAmountResult: Number of items whose time fields were zeroed.
        """
        return ActionAmountResult(**self.client._request("post", "/v1/actions/zero-item-time-fields"))


class AssetsClient:
    """Sub-client for asset-ID based item lookup.

    Accessed via ``HomeboxClient.assets``.
    """

    def __init__(self, client: HomeboxClient):
        self.client = client

    def get_item_by_asset_id(self, id: str) -> PaginationResultRepoItemSummary:
        """Look up an item by its numeric asset ID.

        Args:
            id: The asset ID string (e.g. ``"000001"``).

        Returns:
            PaginationResultRepoItemSummary: Paginated result containing the
                matching item summary, if found.
        """
        return PaginationResultRepoItemSummary(**self.client._request("get", f"/v1/assets/{id}"))


class GroupsClient:
    """Sub-client for group management and statistics endpoints.

    Accessed via ``HomeboxClient.groups``.
    """

    def __init__(self, client: HomeboxClient):
        self.client = client

    def get_group(self) -> Group:
        """Return the current user's group details.

        Returns:
            Group: Group information including name, currency, and timestamps.
        """
        return Group(**self.client._request("get", "/v1/groups"))

    def update_group(self, data: GroupUpdate) -> Group:
        """Update the current group's settings.

        Args:
            data: Fields to update (name and/or currency).

        Returns:
            Group: Updated group information.
        """
        return Group(**self.client._request("put", "/v1/groups", data=data.model_dump()))

    def create_group_invitation(self, data: GroupInvitationCreate) -> GroupInvitation:
        """Create an invitation token that allows new users to join the group.

        Args:
            data: Invitation settings including expiry date and maximum number
                of uses (1–100).

        Returns:
            GroupInvitation: The generated invitation token and its metadata.
        """
        return GroupInvitation(**self.client._request("post", "/v1/groups/invitations", data=data.model_dump()))

    def get_group_statistics(self) -> GroupStatistics:
        """Return aggregate statistics for the current group.

        Returns:
            GroupStatistics: Totals for items, labels, locations, users,
                warranted items, and total item value.
        """
        return GroupStatistics(**self.client._request("get", "/v1/groups/statistics"))

    def get_label_statistics(self) -> list[TotalsByOrganizer]:
        """Return the total item value grouped by label.

        Returns:
            list[TotalsByOrganizer]: One entry per label with the label's ID,
                name, and aggregated total value.
        """
        data = self.client._request("get", "/v1/groups/statistics/labels")
        return [TotalsByOrganizer(**item) for item in data["data"]]

    def get_location_statistics(self) -> list[TotalsByOrganizer]:
        """Return the total item value grouped by location.

        Returns:
            list[TotalsByOrganizer]: One entry per location with the location's
                ID, name, and aggregated total value.
        """
        data = self.client._request("get", "/v1/groups/statistics/locations")

        return [TotalsByOrganizer(**item) for item in data["data"]]

    def get_purchase_price_statistics(self, start: str | None = None, end: str | None = None) -> ValueOverTime:
        """Return the cumulative purchase price of items over a date range.

        Args:
            start: Start date in ``YYYY-MM-DD`` format (inclusive).  Defaults
                to the earliest purchase date when omitted.
            end: End date in ``YYYY-MM-DD`` format (inclusive).  Defaults to
                today when omitted.

        Returns:
            ValueOverTime: Time-series data with individual entries and
                summary values at the start and end of the range.
        """
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return ValueOverTime(**self.client._request("get", "/v1/groups/statistics/purchase-price", params=params))


class ItemsClient:
    """Sub-client for item CRUD, attachment, and maintenance-log endpoints.

    Accessed via ``HomeboxClient.items``.
    """

    def __init__(self, client: HomeboxClient):
        self.client = client

    def query_all_items(
        self,
        q: str | None = None,
        page: int | None = None,
        pageSize: int | None = None,
        labels: list[str] | None = None,
        locations: list[str] | None = None,
        parentIds: list[str] | None = None,
    ) -> PaginationResultRepoItemSummary:
        """Search and paginate all items in the group.

        Args:
            q: Free-text search string.
            page: Page number (1-based).
            pageSize: Number of items per page.
            labels: Filter to items that carry any of the given label IDs.
            locations: Filter to items stored at any of the given location IDs.
            parentIds: Filter to items that are children of the given item IDs.

        Returns:
            PaginationResultRepoItemSummary: Paginated list of matching item
                summaries together with total count and pagination metadata.
        """
        params = {}
        if q:
            params["q"] = q
        if page:
            params["page"] = page
        if pageSize:
            params["pageSize"] = pageSize
        if labels:
            params["labels"] = labels
        if locations:
            params["locations"] = locations
        if parentIds:
            params["parentIds"] = parentIds
        return PaginationResultRepoItemSummary(**self.client._request("get", "/v1/items", params=params))

    def create_item(self, data: ItemCreate) -> ItemSummary:
        """Create a new item.

        Args:
            data: Item creation payload.  ``name`` is required; ``locationId``,
                ``labelIds``, ``description``, ``quantity``, and ``parentId`` are
                optional.

        Returns:
            ItemSummary: Summary representation of the newly created item.
        """
        return ItemSummary(**self.client._request("post", "/v1/items", data=data.model_dump()))

    def export_items(self) -> str:
        """Export all items as a CSV document.

        Returns:
            str: Raw CSV text that can be written to a file or parsed directly.
        """
        return self.client._get("/v1/items/export", binary=False)

    def get_all_custom_field_names(self) -> list[str]:
        """Return the distinct custom field names used across all items.

        Returns:
            list[str]: Sorted list of custom field name strings.
        """
        rest = self.client._request("get", "/v1/items/fields")
        return rest.get("data", [])

    def get_all_custom_field_values(self) -> list[str]:
        """Return the distinct values stored in custom text fields across all items.

        Returns:
            list[str]: List of unique custom field value strings.
        """
        rest = self.client._request("get", "/v1/items/fields/values")
        return rest.get("data", [])

    def import_items(self, csv: bytes):
        """Import items from a CSV file.

        The CSV format matches the one produced by :meth:`export_items`.

        Args:
            csv: Raw CSV bytes to upload (e.g. the contents of an exported
                file opened in binary mode).
        """
        files = {"csv": ("items.csv", csv, "text/csv")}
        self.client._request("post", "/v1/items/import", files=files)

    def get_item(self, id: str) -> ItemOut:
        """Return the full details of a single item.

        Args:
            id: UUID of the item.

        Returns:
            ItemOut: Full item representation including attachments, custom
                fields, maintenance log, and nested location/label information.
        """
        return ItemOut(**self.client._request("get", f"/v1/items/{id}"))

    def update_item(self, id: str, data: ItemUpdate) -> ItemOut:
        """Replace a item's fields with the provided data (full update).

        Args:
            id: UUID of the item to update.
            data: Complete item update payload.  ``name`` is required; all
                other fields are optional.

        Returns:
            ItemOut: Updated full item representation.
        """
        return ItemOut(**self.client._request("put", f"/v1/items/{id}", data=data.model_dump()))

    def delete_item(self, id: str):
        """Permanently delete an item and its attachments.

        Args:
            id: UUID of the item to delete.
        """
        self.client._request("delete", f"/v1/items/{id}")

    def patch_item(self, id: str, data: ItemPatch) -> ItemOut:
        """Partially update an item (only the provided fields are changed).

        Args:
            id: UUID of the item to patch.
            data: Partial update payload (location, labels, or quantity).

        Returns:
            ItemOut: Updated full item representation.
        """
        return ItemOut(**self.client._request("patch", f"/v1/items/{id}", data=data.model_dump()))

    def create_item_attachment(
        self,
        id: str,
        file: bytes,
        type: str | None = None,
        primary: bool | None = None,
        name: str | None = None,
    ) -> ItemOut:
        """Upload a file attachment for an item.

        Args:
            id: UUID of the item to attach the file to.
            file: Raw bytes of the file to upload.
            type: Attachment type (e.g. ``"photo"``, ``"manual"``,
                ``"warranty"``, ``"receipt"``).
            primary: When ``True`` this attachment becomes the item's primary
                image.
            name: Display name / title for the attachment.

        Returns:
            ItemOut: Updated full item representation including the new
                attachment.
        """
        files = {"file": (name or "attachment", file)}
        data = {}
        if type:
            data["type"] = type
        if primary:
            data["primary"] = primary
        if name:
            data["name"] = name
        return ItemOut(**self.client._request("post", f"/v1/items/{id}/attachments", data=data, files=files))

    def get_item_attachment(self, id: str, attachment_id: str) -> bytes:
        """Retrieve a short-lived download token for an item attachment.

        Args:
            id: UUID of the item.
            attachment_id: UUID of the attachment.

        Returns:
            bytes: Raw bytes of the attachment.
        """
        return self.client._get(f"/v1/items/{id}/attachments/{attachment_id}", binary=True)

    def update_item_attachment(self, id: str, attachment_id: str, data: ItemAttachmentUpdate) -> ItemOut:
        """Update metadata for an existing item attachment.

        Args:
            id: UUID of the item.
            attachment_id: UUID of the attachment to update.
            data: Fields to update (title, type, and/or primary flag).

        Returns:
            ItemOut: Updated full item representation.
        """
        return ItemOut(
            **self.client._request("put", f"/v1/items/{id}/attachments/{attachment_id}", data=data.model_dump())
        )

    def delete_item_attachment(self, id: str, attachment_id: str):
        """Delete an attachment from an item.

        Args:
            id: UUID of the item.
            attachment_id: UUID of the attachment to delete.
        """
        self.client._request("delete", f"/v1/items/{id}/attachments/{attachment_id}")

    def duplicate_item(self, id: str, data: DuplicateOptions) -> ItemOut:
        """Create a duplicate of an existing item.

        Args:
            id: UUID of the item to duplicate.
            data: Options controlling which parts to copy (attachments, custom
                fields, maintenance log) and an optional name prefix.

        Returns:
            ItemOut: Full representation of the newly created duplicate item.
        """
        return ItemOut(**self.client._request("post", f"/v1/items/{id}/duplicate", data=data.model_dump()))

    def get_maintenance_log(
        self, id: str, status: MaintenanceFilterStatus | None = None
    ) -> list[MaintenanceEntryWithDetails]:
        """Return the maintenance log for a specific item.

        Args:
            id: UUID of the item.
            status: Optional filter – ``"scheduled"``, ``"completed"``, or
                ``"both"`` (default when omitted).

        Returns:
            list[MaintenanceEntryWithDetails]: Maintenance entries with item
                context information attached.
        """
        params = {}
        if status:
            params["status"] = status.value
        data = self.client._request("get", f"/v1/items/{id}/maintenance", params=params)
        return [MaintenanceEntryWithDetails(**item) for item in data.get("data", [])]

    def create_maintenance_entry(self, id: str, data: MaintenanceEntryCreate) -> MaintenanceEntry:
        """Add a maintenance log entry to an item.

        Args:
            id: UUID of the item.
            data: Maintenance entry data.  ``name`` is required; ``description``,
                ``cost``, ``scheduledDate``, and ``completedDate`` are optional.

        Returns:
            MaintenanceEntry: The newly created maintenance entry.
        """
        return MaintenanceEntry(**self.client._request("post", f"/v1/items/{id}/maintenance", data=data.model_dump()))

    def get_item_path(self, id: str) -> list[ItemPath]:
        """Return the ancestry path of an item (from root to the item itself).

        Useful for building breadcrumb navigation in applications.

        Args:
            id: UUID of the item.

        Returns:
            list[ItemPath]: Ordered list of path nodes.  Each node carries an
                ``id``, ``name``, and ``type`` (``"location"`` or ``"item"``).
        """
        data = self.client._request("get", f"/v1/items/{id}/path")
        return [ItemPath(**item) for item in data.get("data", [])]


class LabelsClient:
    """Sub-client for label management endpoints.

    Accessed via ``HomeboxClient.labels``.
    """

    def __init__(self, client: HomeboxClient):
        self.client = client

    def get_all_labels(self) -> list[LabelOut]:
        """Return all labels defined in the group.

        Returns:
            list[LabelOut]: Every label with its ID, name, colour, description,
                and timestamps.
        """
        data = self.client._request("get", "/v1/labels")
        return [LabelOut(**item) for item in data.get("data", [])]

    def create_label(self, data: LabelCreate) -> LabelSummary:
        """Create a new label.

        Args:
            data: Label creation payload.  ``name`` is required; ``color`` and
                ``description`` are optional.

        Returns:
            LabelSummary: Summary representation of the newly created label.
        """
        return LabelSummary(**self.client._request("post", "/v1/labels", data=data.model_dump()))

    def get_label(self, id: str) -> LabelOut:
        """Return the details of a single label.

        Args:
            id: UUID of the label.

        Returns:
            LabelOut: Full label representation.
        """
        return LabelOut(**self.client._request("get", f"/v1/labels/{id}"))

    def update_label(self, id: str, data: LabelOut) -> LabelOut:
        """Replace a label's fields with the provided data.

        Args:
            id: UUID of the label to update.
            data: Updated label payload.

        Returns:
            LabelOut: Updated label representation.
        """
        return LabelOut(**self.client._request("put", f"/v1/labels/{id}", data=data.model_dump()))

    def delete_label(self, id: str):
        """Permanently delete a label.

        Deleting a label does **not** delete the items associated with it.

        Args:
            id: UUID of the label to delete.
        """
        self.client._request("delete", f"/v1/labels/{id}")


class LocationsClient:
    """Sub-client for location management endpoints.

    Accessed via ``HomeboxClient.locations``.
    """

    def __init__(self, client: HomeboxClient):
        self.client = client

    def get_all_locations(self, filterChildren: bool | None = None) -> list[LocationOutCount]:
        """Return all locations in the group.

        Args:
            filterChildren: When ``True`` only top-level (root) locations are
                returned; nested child locations are excluded.

        Returns:
            list[LocationOutCount]: Each location summary includes an
                ``itemCount`` field with the number of items stored there.
        """
        params = {}
        if filterChildren is not None:
            params["filterChildren"] = filterChildren
        data = self.client._request("get", "/v1/locations", params=params)
        return [LocationOutCount(**item) for item in data["data"]]

    def create_location(self, data: LocationCreate) -> LocationSummary:
        """Create a new location.

        Args:
            data: Location creation payload.  ``name`` is optional; you can also
                supply ``description`` and a ``parentId`` to nest it under an
                existing location.

        Returns:
            LocationSummary: Summary representation of the newly created location.
        """
        return LocationSummary(**self.client._request("post", "/v1/locations", data=data.model_dump()))

    def get_locations_tree(self, withItems: bool | None = None) -> list[TreeItem]:
        """Return all locations as a nested tree structure.

        Args:
            withItems: When ``True`` items are embedded as leaf nodes in the
                tree alongside child locations.

        Returns:
            list[TreeItem]: Root-level tree nodes; each node may have a
                ``children`` list of nested nodes.
        """
        params = {}
        if withItems:
            params["withItems"] = withItems
        data = self.client._request("get", "/v1/locations/tree", params=params)
        return [TreeItem(**item) for item in data.get("data", [])]

    def get_location(self, id: str) -> LocationOut:
        """Return the details of a single location.

        Args:
            id: UUID of the location.

        Returns:
            LocationOut: Full location representation including parent summary,
                child summaries, and total item price.
        """
        return LocationOut(**self.client._request("get", f"/v1/locations/{id}"))

    def update_location(self, id: str, data: LocationUpdate) -> LocationOut:
        """Replace a location's fields with the provided data.

        Args:
            id: UUID of the location to update.
            data: Updated location payload (name, description, parentId).

        Returns:
            LocationOut: Updated full location representation.
        """
        return LocationOut(**self.client._request("put", f"/v1/locations/{id}", data=data.model_dump()))

    def delete_location(self, id: str):
        """Permanently delete a location.

        Args:
            id: UUID of the location to delete.
        """
        self.client._request("delete", f"/v1/locations/{id}")


class MaintenanceClient:
    """Sub-client for cross-item maintenance-log endpoints.

    Accessed via ``HomeboxClient.maintenance``.
    """

    def __init__(self, client: HomeboxClient):
        self.client = client

    def query_all_maintenance(self, status: MaintenanceFilterStatus | None = None) -> list[MaintenanceEntryWithDetails]:
        """Return maintenance entries across all items, optionally filtered by status.

        Args:
            status: Optional status filter – ``MaintenanceFilterStatus.MaintenanceFilterStatusScheduled``,
                ``MaintenanceFilterStatus.MaintenanceFilterStatusCompleted``, or
                ``MaintenanceFilterStatus.MaintenanceFilterStatusBoth`` (default).

        Returns:
            list[MaintenanceEntryWithDetails]: All matching maintenance entries
                including their parent item ID and name.
        """
        params = {}
        if status:
            params["status"] = status.value
        data = self.client._request("get", "/v1/maintenance", params=params)
        return [MaintenanceEntryWithDetails(**item) for item in data.get("data", [])]

    def update_maintenance_entry(self, id: str, data: MaintenanceEntryUpdate) -> MaintenanceEntry:
        """Update an existing maintenance entry.

        Args:
            id: UUID of the maintenance entry to update.
            data: Updated maintenance entry fields.

        Returns:
            MaintenanceEntry: Updated maintenance entry.
        """
        return MaintenanceEntry(**self.client._request("put", f"/v1/maintenance/{id}", data=data.model_dump()))

    def delete_maintenance_entry(self, id: str):
        """Permanently delete a maintenance entry.

        Args:
            id: UUID of the maintenance entry to delete.
        """
        self.client._request("delete", f"/v1/maintenance/{id}")


class NotifiersClient:
    """Sub-client for notification-channel (notifier) endpoints.

    Accessed via ``HomeboxClient.notifiers``.
    """

    def __init__(self, client: HomeboxClient):
        self.client = client

    def get_notifiers(self) -> list[NotifierOut]:
        """Return all notification channels configured for the current user.

        Returns:
            list[NotifierOut]: Each notifier includes its ID, name, webhook URL,
                active flag, and group/user association.
        """
        data = self.client._request("get", "/v1/notifiers")
        return [NotifierOut(**item) for item in data.get("data", [])]

    def create_notifier(self, data: NotifierCreate) -> NotifierOut:
        """Create a new notification channel.

        Args:
            data: Notifier creation payload.  ``name`` and ``url`` (webhook) are
                required; ``isActive`` defaults to server-side behaviour when
                omitted.

        Returns:
            NotifierOut: Representation of the newly created notifier.
        """
        return NotifierOut(**self.client._request("post", "/v1/notifiers", data=data.model_dump()))

    def test_notifier(self, url: str):
        """Send a test notification to the given webhook URL.

        Args:
            url: Webhook URL to test (does not need to match an existing
                notifier).
        """
        params = {"url": url}
        self.client._request("post", "/v1/notifiers/test", params=params)

    def update_notifier(self, id: str, data: NotifierUpdate) -> NotifierOut:
        """Replace a notifier's settings with the provided data.

        Args:
            id: UUID of the notifier to update.
            data: Updated notifier payload.  ``name`` is required; ``url`` and
                ``isActive`` are optional.

        Returns:
            NotifierOut: Updated notifier representation.
        """
        return NotifierOut(**self.client._request("put", f"/v1/notifiers/{id}", data=data.model_dump()))

    def delete_notifier(self, id: str):
        """Permanently delete a notification channel.

        Args:
            id: UUID of the notifier to delete.
        """
        self.client._request("delete", f"/v1/notifiers/{id}")


class UsersClient:
    """Sub-client for user account management endpoints.

    Accessed via ``HomeboxClient.users``.
    """

    def __init__(self, client: HomeboxClient):
        self.client = client

    def change_password(self, data: ChangePassword):
        """Change the current user's password.

        Args:
            data: Password change payload containing ``current`` and ``new``
                password strings.
        """
        self.client._request("put", "/v1/users/change-password", data=data.model_dump())

    def user_logout(self):
        """Invalidate the current session token on the server side."""
        self.client._request("post", "/v1/users/logout")

    def user_token_refresh(self) -> TokenResponse:
        """Refresh the current Bearer token and return a new one.

        Returns:
            TokenResponse: New token with updated expiry.
        """
        return TokenResponse(**self.client._request("get", "/v1/users/refresh"))

    def oidc_login(self, timeout: float | None = None) -> str | None:
        """Initiate OIDC login and return the provider redirect URL.

        Args:
            timeout: Optional request timeout in seconds.

        Returns:
            str | None: Location header value for the OIDC redirect, if
                present.
        """
        response = requests.get(
            f"{self.client.base_url}/v1/users/login/oidc",
            headers=self.client.headers.copy(),
            allow_redirects=False,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.headers.get("Location")

    def oidc_callback(self, code: str, state: str, timeout: float | None = None) -> str | None:
        """Call the OIDC callback endpoint and return the redirect location.

        Args:
            code: Authorization code received from the OIDC provider.
            state: State value returned by the OIDC provider.
            timeout: Optional request timeout in seconds.

        Returns:
            str | None: Location header value returned by Homebox.
        """
        params = {"code": code, "state": state}
        response = requests.get(
            f"{self.client.base_url}/v1/users/login/oidc/callback",
            params=params,
            headers=self.client.headers.copy(),
            allow_redirects=False,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.headers.get("Location")

    def register_new_user(self, data: UserRegistration):
        """Register a new user account.

        Requires either open registration to be enabled on the server, or a
        valid group invitation token included in ``data``.

        Args:
            data: Registration payload containing ``name``, ``email``,
                ``password``, and an optional invitation ``token``.
        """
        self.client._request("post", "/v1/users/register", data=data.model_dump())

    def get_user_self(self) -> UserOut:
        """Return the profile of the currently authenticated user.

        Returns:
            UserOut: User details including ID, name, email, group association,
                and role flags.
        """
        return UserOut(**self.client._request("get", "/v1/users/self")["item"])

    def update_account(self, data: UserUpdate) -> UserUpdate:
        """Update the current user's profile information.

        Args:
            data: Fields to update (``name`` and/or ``email``).

        Returns:
            UserUpdate: The updated profile data as echoed by the server.
        """
        return UserUpdate(**self.client._request("put", "/v1/users/self", data=data.model_dump())["item"])

    def delete_account(self):
        """Permanently delete the current user's account.

        This action is irreversible and will also remove the user from their
        group.
        """
        self.client._request("delete", "/v1/users/self")


class ReportingClient:
    """Sub-client for reporting and export endpoints.

    Accessed via ``HomeboxClient.reporting``.
    """

    def __init__(self, client: HomeboxClient):
        self.client = client

    def export_bill_of_materials(self) -> str:
        """Export a Bill of Materials (BOM) report for all items in the group.

        Returns:
            str: Raw CSV-formatted Bill of Materials report.
        """
        return self.client._get("/v1/reporting/bill-of-materials", binary=False)


class TemplatesClient:
    """Sub-client for item template endpoints.

    Accessed via ``HomeboxClient.templates``.
    """

    def __init__(self, client: HomeboxClient):
        self.client = client

    def get_all_templates(self) -> list[ItemTemplateSummary]:
        """Return all item templates in the current group."""
        data = self.client._request("get", "/v1/templates")
        return [ItemTemplateSummary(**item) for item in data.get("data", [])]

    def create_template(self, data: ItemTemplateCreate) -> ItemTemplateOut:
        """Create a new item template."""
        return ItemTemplateOut(**self.client._request("post", "/v1/templates", data=data.model_dump()))

    def get_template(self, id: str) -> ItemTemplateOut:
        """Return a single item template by ID."""
        return ItemTemplateOut(**self.client._request("get", f"/v1/templates/{id}"))

    def update_template(self, id: str, data: ItemTemplateUpdate) -> ItemTemplateOut:
        """Update an existing item template."""
        return ItemTemplateOut(**self.client._request("put", f"/v1/templates/{id}", data=data.model_dump()))

    def delete_template(self, id: str):
        """Delete an item template."""
        self.client._request("delete", f"/v1/templates/{id}")

    def create_item_from_template(self, id: str, data: ItemTemplateCreateItemRequest) -> ItemOut:
        """Create an item from the specified template."""
        return ItemOut(**self.client._request("post", f"/v1/templates/{id}/create-item", data=data.model_dump()))


class LabelMakerClient:
    """Sub-client for printable label generation endpoints.

    Accessed via ``HomeboxClient.labelmaker``.
    """

    def __init__(self, client: HomeboxClient):
        self.client = client

    def get_asset_label(self, id: str, print: bool | None = None) -> bytes:
        """Return a printable label for an asset identified by its asset ID.

        Args:
            id: Asset ID string.
            print: When ``True`` the server returns a print-ready version of the
                label.

        Returns:
            bytes: Label content (typically SVG or HTML).
        """
        params = {}
        if print:
            params["print"] = print
        return self.client._get(f"/v1/labelmaker/assets/{id}", params=params, binary=True)

    def get_item_label(self, id: str, print: bool | None = None) -> bytes:
        """Return a printable label for an item.

        Args:
            id: UUID of the item.
            print: When ``True`` the server returns a print-ready version of the
                label.

        Returns:
            bytes: Label content (typically SVG or HTML).
        """
        params = {}
        if print:
            params["print"] = print
        return self.client._get(f"/v1/labelmaker/item/{id}", params=params, binary=True)

    def get_location_label(self, id: str, print: bool | None = None) -> bytes:
        """Return a printable label for a location.

        Args:
            id: UUID of the location.
            print: When ``True`` the server returns a print-ready version of the
                label.

        Returns:
            str: Label content (typically SVG or HTML).
        """
        params = {}
        if print:
            params["print"] = print
        return self.client._get(f"/v1/labelmaker/location/{id}", params=params, binary=True)


class ProductsClient:
    """Sub-client for barcode / QR-code product lookup endpoints.

    Accessed via ``HomeboxClient.products``.
    """

    def __init__(self, client: HomeboxClient):
        self.client = client

    def search_ean_from_barcode(self, data: str | None = None) -> list[BarcodeProduct]:
        """Look up product information by EAN/barcode string.

        Queries external product databases and returns matching product details
        that can be used to pre-fill a new item.

        Args:
            data: EAN-13 or other barcode string to look up.

        Returns:
            list[BarcodeProduct]: Matching products from one or more search
                engines.  Each result may include manufacturer, model number,
                notes, an image, and a pre-populated :class:`ItemCreate` payload.
        """
        params = {}
        if data:
            params["data"] = data
        resp = self.client._request("get", "/v1/products/search-from-barcode", params=params)
        return [BarcodeProduct(**item) for item in resp.get("data", [])]

    def create_qr_code(self, data: str | None = None) -> bytes:
        """Generate a QR code image for an arbitrary string.

        Args:
            data: The string to encode in the QR code (e.g. a URL or asset ID).

        Returns:
            bytes: QR code image content (SVG or PNG depending on server config).
        """
        params = {}
        if data:
            params["data"] = data
        return self.client._get("/v1/qrcode", params=params, binary=True)
