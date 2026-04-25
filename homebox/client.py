"""Client classes for interacting with the Homebox REST API."""

from __future__ import annotations

import os
from typing import Any, Optional

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
    ItemAttachmentToken,
    ItemAttachmentUpdate,
    ItemCreate,
    ItemOut,
    ItemPatch,
    ItemPath,
    ItemSummary,
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
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        base_url = base_url or os.environ.get("HOMEBOX_URL")
        if not base_url:
            raise ValueError("base_url must be provided or the HOMEBOX_URL environment variable must be set")
        token = token or os.environ.get("HOMEBOX_TOKEN")
        self.base_url = base_url
        self.token = token
        self.headers = {"Content-Type": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

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

    def _request(self, method, endpoint, params=None, data=None, files=None, timeout=None) -> dict[Any, Any]:
        headers = self.headers.copy()
        if files:
            del headers["Content-Type"]

        response = requests.request(
            method,
            f"{self.base_url}{endpoint}",
            params=params,
            json=data,
            files=files,
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()

        if response.status_code == 204:
            return {}

        result = response.json()
        if isinstance(result, list):
            return {"data": result}
        return result

    def _get(self, endpoint, params=None, data=None, files=None, timeout=None) -> str:
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()
        if files:
            del headers["Content-Type"]

        response = requests.get(url, params=params, json=data, files=files, headers=headers, timeout=timeout)
        response.raise_for_status()

        if response.status_code == 204:
            return ""

        return response.text

    def login(self, username, password, stay_logged_in=False, provider=None):
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
        self.headers["Authorization"] = f"Bearer {self.token}"
        return token_response

    def currency(self):
        return Currency(**self._request("get", "/v1/currency"))

    def application_info(self):
        return APISummary(**self._request("get", "/v1/status"))


class ActionsClient:
    def __init__(self, client: HomeboxClient):
        self.client = client

    def create_missing_thumbnails(self) -> ActionAmountResult:
        return ActionAmountResult(**self.client._request("post", "/v1/actions/create-missing-thumbnails"))

    def ensure_asset_ids(self) -> ActionAmountResult:
        return ActionAmountResult(**self.client._request("post", "/v1/actions/ensure-asset-ids"))

    def ensure_import_refs(self) -> ActionAmountResult:
        return ActionAmountResult(**self.client._request("post", "/v1/actions/ensure-import-refs"))

    def set_primary_photos(self) -> ActionAmountResult:
        return ActionAmountResult(**self.client._request("post", "/v1/actions/set-primary-photos"))

    def zero_out_time_fields(self) -> ActionAmountResult:
        return ActionAmountResult(**self.client._request("post", "/v1/actions/zero-item-time-fields"))


class AssetsClient:
    def __init__(self, client: HomeboxClient):
        self.client = client

    def get_item_by_asset_id(self, id: str) -> PaginationResultRepoItemSummary:
        return PaginationResultRepoItemSummary(**self.client._request("get", f"/v1/assets/{id}"))


class GroupsClient:
    def __init__(self, client: HomeboxClient):
        self.client = client

    def get_group(self) -> Group:
        return Group(**self.client._request("get", "/v1/groups"))

    def update_group(self, data: GroupUpdate) -> Group:
        return Group(**self.client._request("put", "/v1/groups", data=data.model_dump()))

    def create_group_invitation(self, data: GroupInvitationCreate) -> GroupInvitation:
        return GroupInvitation(**self.client._request("post", "/v1/groups/invitations", data=data.model_dump()))

    def get_group_statistics(self) -> GroupStatistics:
        return GroupStatistics(**self.client._request("get", "/v1/groups/statistics"))

    def get_label_statistics(self) -> list[TotalsByOrganizer]:
        return [TotalsByOrganizer(**item) for item in self.client._request("get", "/v1/groups/statistics/labels")]

    def get_location_statistics(self) -> list[TotalsByOrganizer]:
        return [TotalsByOrganizer(**item) for item in self.client._request("get", "/v1/groups/statistics/locations")]

    def get_purchase_price_statistics(self, start: str | None = None, end: str | None = None) -> ValueOverTime:
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return ValueOverTime(**self.client._request("get", "/v1/groups/statistics/purchase-price", params=params))


class ItemsClient:
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
        return ItemSummary(**self.client._request("post", "/v1/items", data=data.model_dump()))

    def export_items(self) -> str:
        return self.client._get("/v1/items/export")

    def get_all_custom_field_names(self) -> list[str]:
        rest = self.client._request("get", "/v1/items/fields")
        return rest.get("data", [])

    def get_all_custom_field_values(self) -> list[str]:
        rest = self.client._request("get", "/v1/items/fields/values")
        return rest.get("data", [])

    def import_items(self, csv: bytes):
        files = {"csv": csv}
        self.client._request("post", "/v1/items/import", files=files)

    def get_item(self, id: str) -> ItemOut:
        return ItemOut(**self.client._request("get", f"/v1/items/{id}"))

    def update_item(self, id: str, data: ItemUpdate) -> ItemOut:
        return ItemOut(**self.client._request("put", f"/v1/items/{id}", data=data.model_dump()))

    def delete_item(self, id: str):
        self.client._request("delete", f"/v1/items/{id}")

    def patch_item(self, id: str, data: ItemPatch) -> ItemOut:
        return ItemOut(**self.client._request("patch", f"/v1/items/{id}", data=data.model_dump()))

    def create_item_attachment(
        self,
        id: str,
        file: bytes,
        type: str | None = None,
        primary: bool | None = None,
        name: str | None = None,
    ) -> ItemOut:
        files = {"file": file}
        data = {}
        if type:
            data["type"] = type
        if primary:
            data["primary"] = primary
        if name:
            data["name"] = name
        return ItemOut(**self.client._request("post", f"/v1/items/{id}/attachments", data=data, files=files))

    def get_item_attachment(self, id: str, attachment_id: str) -> ItemAttachmentToken:
        return ItemAttachmentToken(**self.client._request("get", f"/v1/items/{id}/attachments/{attachment_id}"))

    def update_item_attachment(self, id: str, attachment_id: str, data: ItemAttachmentUpdate) -> ItemOut:
        return ItemOut(
            **self.client._request("put", f"/v1/items/{id}/attachments/{attachment_id}", data=data.model_dump())
        )

    def delete_item_attachment(self, id: str, attachment_id: str):
        self.client._request("delete", f"/v1/items/{id}/attachments/{attachment_id}")

    def duplicate_item(self, id: str, data: DuplicateOptions) -> ItemOut:
        return ItemOut(**self.client._request("post", f"/v1/items/{id}/duplicate", data=data.model_dump()))

    def get_maintenance_log(
        self, id: str, status: MaintenanceFilterStatus | None = None
    ) -> list[MaintenanceEntryWithDetails]:
        params = {}
        if status:
            params["status"] = status.value
        return [
            MaintenanceEntryWithDetails(**item)
            for item in self.client._request("get", f"/v1/items/{id}/maintenance", params=params)
        ]

    def create_maintenance_entry(self, id: str, data: MaintenanceEntryCreate) -> MaintenanceEntry:
        return MaintenanceEntry(**self.client._request("post", f"/v1/items/{id}/maintenance", data=data.model_dump()))

    def get_item_path(self, id: str) -> list[ItemPath]:
        return [ItemPath(**item) for item in self.client._request("get", f"/v1/items/{id}/path")]


class LabelsClient:
    def __init__(self, client: HomeboxClient):
        self.client = client

    def get_all_labels(self) -> list[LabelOut]:
        return [LabelOut(**item) for item in self.client._request("get", "/v1/labels")]

    def create_label(self, data: LabelCreate) -> LabelSummary:
        return LabelSummary(**self.client._request("post", "/v1/labels", data=data.model_dump()))

    def get_label(self, id: str) -> LabelOut:
        return LabelOut(**self.client._request("get", f"/v1/labels/{id}"))

    def update_label(self, id: str, data: LabelOut) -> LabelOut:
        return LabelOut(**self.client._request("put", f"/v1/labels/{id}", data=data.model_dump()))

    def delete_label(self, id: str):
        self.client._request("delete", f"/v1/labels/{id}")


class LocationsClient:
    def __init__(self, client: HomeboxClient):
        self.client = client

    def get_all_locations(self, filterChildren: bool | None = None) -> list[LocationOutCount]:
        params = {}
        if filterChildren is not None:
            params["filterChildren"] = filterChildren
        return [LocationOutCount(**item) for item in self.client._request("get", "/v1/locations", params=params)]

    def create_location(self, data: LocationCreate) -> LocationSummary:
        return LocationSummary(**self.client._request("post", "/v1/locations", data=data.model_dump()))

    def get_locations_tree(self, withItems: bool | None = None) -> list[TreeItem]:
        params = {}
        if withItems:
            params["withItems"] = withItems
        return [TreeItem(**item) for item in self.client._request("get", "/v1/locations/tree", params=params)]

    def get_location(self, id: str) -> LocationOut:
        return LocationOut(**self.client._request("get", f"/v1/locations/{id}"))

    def update_location(self, id: str, data: LocationUpdate) -> LocationOut:
        return LocationOut(**self.client._request("put", f"/v1/locations/{id}", data=data.model_dump()))

    def delete_location(self, id: str):
        self.client._request("delete", f"/v1/locations/{id}")


class MaintenanceClient:
    def __init__(self, client: HomeboxClient):
        self.client = client

    def query_all_maintenance(self, status: MaintenanceFilterStatus | None = None) -> list[MaintenanceEntryWithDetails]:
        params = {}
        if status:
            params["status"] = status.value
        return [
            MaintenanceEntryWithDetails(**item)
            for item in self.client._request("get", "/v1/maintenance", params=params)
        ]

    def update_maintenance_entry(self, id: str, data: MaintenanceEntryUpdate) -> MaintenanceEntry:
        return MaintenanceEntry(**self.client._request("put", f"/v1/maintenance/{id}", data=data.model_dump()))

    def delete_maintenance_entry(self, id: str):
        self.client._request("delete", f"/v1/maintenance/{id}")


class NotifiersClient:
    def __init__(self, client: HomeboxClient):
        self.client = client

    def get_notifiers(self) -> list[NotifierOut]:
        return [NotifierOut(**item) for item in self.client._request("get", "/v1/notifiers")]

    def create_notifier(self, data: NotifierCreate) -> NotifierOut:
        return NotifierOut(**self.client._request("post", "/v1/notifiers", data=data.model_dump()))

    def test_notifier(self, url: str):
        params = {"url": url}
        self.client._request("post", "/v1/notifiers/test", params=params)

    def update_notifier(self, id: str, data: NotifierUpdate) -> NotifierOut:
        return NotifierOut(**self.client._request("put", f"/v1/notifiers/{id}", data=data.model_dump()))

    def delete_notifier(self, id: str):
        self.client._request("delete", f"/v1/notifiers/{id}")


class UsersClient:
    def __init__(self, client: HomeboxClient):
        self.client = client

    def change_password(self, data: ChangePassword):
        self.client._request("put", "/v1/users/change-password", data=data.model_dump())

    def user_logout(self):
        self.client._request("post", "/v1/users/logout")

    def user_token_refresh(self) -> TokenResponse:
        return TokenResponse(**self.client._request("get", "/v1/users/refresh"))

    def register_new_user(self, data: UserRegistration):
        self.client._request("post", "/v1/users/register", data=data.model_dump())

    def get_user_self(self) -> UserOut:
        return UserOut(**self.client._request("get", "/v1/users/self")["item"])

    def update_account(self, data: UserUpdate) -> UserUpdate:
        return UserUpdate(**self.client._request("put", "/v1/users/self", data=data.model_dump())["item"])

    def delete_account(self):
        self.client._request("delete", "/v1/users/self")


class ReportingClient:
    def __init__(self, client: HomeboxClient):
        self.client = client

    def export_bill_of_materials(self) -> str:
        return self.client._get("/v1/reporting/bill-of-materials")


class LabelMakerClient:
    def __init__(self, client: HomeboxClient):
        self.client = client

    def get_asset_label(self, id: str, print: bool | None = None) -> str:
        params = {}
        if print:
            params["print"] = print
        return self.client._get(f"/v1/labelmaker/assets/{id}", params=params)

    def get_item_label(self, id: str, print: bool | None = None) -> str:
        params = {}
        if print:
            params["print"] = print
        return self.client._get(f"/v1/labelmaker/item/{id}", params=params)

    def get_location_label(self, id: str, print: bool | None = None) -> str:
        params = {}
        if print:
            params["print"] = print
        return self.client._get(f"/v1/labelmaker/location/{id}", params=params)


class ProductsClient:
    def __init__(self, client: HomeboxClient):
        self.client = client

    def search_ean_from_barcode(self, data: str | None = None) -> list[BarcodeProduct]:
        params = {}
        if data:
            params["data"] = data
        return [
            BarcodeProduct(**item)
            for item in self.client._request("get", "/v1/products/search-from-barcode", params=params)
        ]

    def create_qr_code(self, data: str | None = None) -> str:
        params = {}
        if data:
            params["data"] = data
        return self.client._get("/v1/qrcode", params=params)
