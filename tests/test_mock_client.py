"""Tests for HomeboxClient core, optional parameters, error handling, and edge cases."""

import pytest
import requests
from unittest.mock import MagicMock, patch
from homebox.client import HomeboxClient
from homebox import models
from homebox.models.types import MaintenanceFilterStatus


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


@pytest.fixture
def authed_client():
    return HomeboxClient(base_url="http://localhost:8080", token="test-token")


# ---------------------------------------------------------------------------
# HomeboxClient constructor
# ---------------------------------------------------------------------------


def test_client_without_token():
    c = HomeboxClient(base_url="http://localhost:8080")
    assert c.token is None
    assert "Authorization" not in c.headers
    assert c.headers["Content-Type"] == "application/json"


def test_client_with_token():
    c = HomeboxClient(base_url="http://localhost:8080", token="mytoken")
    assert c.token == "mytoken"
    assert c.headers["Authorization"] == "Bearer mytoken"


def test_client_sub_clients_initialized(client):
    assert client.actions is not None
    assert client.assets is not None
    assert client.groups is not None
    assert client.items is not None
    assert client.labels is not None
    assert client.locations is not None
    assert client.maintenance is not None
    assert client.notifiers is not None
    assert client.users is not None
    assert client.reporting is not None
    assert client.labelmaker is not None
    assert client.products is not None


# ---------------------------------------------------------------------------
# HomeboxClient._request
# ---------------------------------------------------------------------------


def test_request_raises_on_http_error(client):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
    with patch("requests.request", return_value=mock_response):
        with pytest.raises(requests.HTTPError):
            client._request("get", "/v1/items")


def test_request_returns_none_on_204(client):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 204
    with patch("requests.request", return_value=mock_response):
        result = client._request("delete", "/v1/items/1")
    assert result is None


def test_request_returns_json_on_200(client):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "1"}
    with patch("requests.request", return_value=mock_response):
        result = client._request("get", "/v1/items/1")
    assert result == {"id": "1"}


def test_request_with_files_removes_content_type(authed_client):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "1", "name": "Test"}
    with patch("requests.request", return_value=mock_response) as mock_req:
        authed_client._request("post", "/v1/items/1/attachments", files={"file": b"data"})
    call_kwargs = mock_req.call_args
    assert "Content-Type" not in call_kwargs[1]["headers"]


def test_request_url_construction(client):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    with patch("requests.request", return_value=mock_response) as mock_req:
        client._request("get", "/v1/items")
    mock_req.assert_called_once()
    assert mock_req.call_args[0][1] == "http://localhost:8080/v1/items"


# ---------------------------------------------------------------------------
# HomeboxClient.login
# ---------------------------------------------------------------------------


def test_login_sets_token(client):
    mocker_response = {"token": "new-token", "expiresAt": None, "attachmentToken": None}
    with patch.object(client, "_request", return_value=mocker_response):
        result = client.login("user@example.com", "password")
    assert result.token == "new-token"
    assert client.token == "new-token"
    assert client.headers["Authorization"] == "Bearer new-token"


def test_login_with_provider(client):
    mocker_response = {"token": "new-token"}
    with patch.object(client, "_request", return_value=mocker_response) as mock_req:
        client.login("user@example.com", "password", provider="oauth")
    call_kwargs = mock_req.call_args
    assert call_kwargs[1]["params"]["provider"] == "oauth"


def test_login_without_provider_no_params(client):
    mocker_response = {"token": "new-token"}
    with patch.object(client, "_request", return_value=mocker_response) as mock_req:
        client.login("user@example.com", "password")
    call_kwargs = mock_req.call_args
    assert call_kwargs[1]["params"] == {}


def test_login_stay_logged_in(client):
    mocker_response = {"token": "new-token"}
    with patch.object(client, "_request", return_value=mocker_response) as mock_req:
        client.login("user@example.com", "password", stay_logged_in=True)
    call_kwargs = mock_req.call_args
    login_data = call_kwargs[1]["data"]
    assert login_data["stayLoggedIn"] is True


# ---------------------------------------------------------------------------
# HomeboxClient.currency and application_info
# ---------------------------------------------------------------------------


def test_currency(client):
    with patch.object(client, "_request", return_value={"code": "USD", "name": "Dollar"}):
        result = client.currency()
    assert isinstance(result, models.Currency)


def test_application_info(client):
    with patch.object(
        client,
        "_request",
        return_value={"health": True, "demo": False, "allowRegistration": True},
    ):
        result = client.application_info()
    assert isinstance(result, models.APISummary)
    assert result.health is True


# ---------------------------------------------------------------------------
# ItemsClient - optional parameters
# ---------------------------------------------------------------------------


def test_query_all_items_with_all_params(mocker, client):
    mocker.patch.object(
        client,
        "_request",
        return_value={"items": [], "page": 2, "pageSize": 20, "total": 0},
    )
    result = client.items.query_all_items(
        q="test",
        page=2,
        pageSize=20,
        labels=["label1"],
        locations=["loc1"],
        parentIds=["parent1"],
    )
    assert result.page == 2
    assert result.pageSize == 20


def test_query_all_items_empty_result(mocker, client):
    mocker.patch.object(
        client,
        "_request",
        return_value={"items": [], "page": 1, "pageSize": 10, "total": 0},
    )
    result = client.items.query_all_items()
    assert result.items == []
    assert result.total == 0


def test_create_item_attachment_with_type_and_primary(mocker, client):
    mocker.patch.object(
        client, "_request", return_value={"id": "1", "name": "Test Item"}
    )
    result = client.items.create_item_attachment(
        "1", b"file", type="photo", primary=True, name="photo.jpg"
    )
    assert result.id == "1"


def test_get_maintenance_log_with_status(mocker, client):
    mocker.patch.object(
        client, "_request", return_value=[{"id": "1", "name": "Scheduled Entry"}]
    )
    result = client.items.get_maintenance_log(
        "1", status=MaintenanceFilterStatus.MaintenanceFilterStatusScheduled
    )
    assert len(result) == 1


def test_get_maintenance_log_completed_status(mocker, client):
    mocker.patch.object(client, "_request", return_value=[])
    result = client.items.get_maintenance_log(
        "1", status=MaintenanceFilterStatus.MaintenanceFilterStatusCompleted
    )
    assert result == []


def test_get_maintenance_log_both_status(mocker, client):
    mocker.patch.object(
        client,
        "_request",
        return_value=[
            {"id": "1", "name": "Entry1"},
            {"id": "2", "name": "Entry2"},
        ],
    )
    result = client.items.get_maintenance_log(
        "1", status=MaintenanceFilterStatus.MaintenanceFilterStatusBoth
    )
    assert len(result) == 2


def test_get_maintenance_log_empty(mocker, client):
    mocker.patch.object(client, "_request", return_value=[])
    result = client.items.get_maintenance_log("1")
    assert result == []


def test_get_item_path_empty(mocker, client):
    mocker.patch.object(client, "_request", return_value=[])
    result = client.items.get_item_path("1")
    assert result == []


def test_get_item_path_multiple(mocker, client):
    mocker.patch.object(
        client,
        "_request",
        return_value=[
            {"id": "10", "name": "Parent", "type": "location"},
            {"id": "1", "name": "Item", "type": "item"},
        ],
    )
    result = client.items.get_item_path("1")
    assert len(result) == 2
    assert result[0].type.value == "location"
    assert result[1].type.value == "item"


# ---------------------------------------------------------------------------
# GroupsClient - optional parameters
# ---------------------------------------------------------------------------


def test_get_purchase_price_statistics_with_start(mocker, client):
    mocker.patch.object(
        client, "_request", return_value={"valueAtStart": 50, "valueAtEnd": 100}
    )
    result = client.groups.get_purchase_price_statistics(start="2024-01-01")
    assert result.valueAtStart == 50


def test_get_purchase_price_statistics_with_end(mocker, client):
    mocker.patch.object(
        client, "_request", return_value={"valueAtStart": 50, "valueAtEnd": 200}
    )
    result = client.groups.get_purchase_price_statistics(end="2024-12-31")
    assert result.valueAtEnd == 200


def test_get_purchase_price_statistics_with_both(mocker, client):
    mocker.patch.object(
        client, "_request", return_value={"valueAtStart": 50, "valueAtEnd": 200}
    )
    result = client.groups.get_purchase_price_statistics(
        start="2024-01-01", end="2024-12-31"
    )
    assert result.valueAtStart == 50
    assert result.valueAtEnd == 200


def test_get_label_statistics_empty(mocker, client):
    mocker.patch.object(client, "_request", return_value=[])
    result = client.groups.get_label_statistics()
    assert result == []


def test_get_location_statistics_empty(mocker, client):
    mocker.patch.object(client, "_request", return_value=[])
    result = client.groups.get_location_statistics()
    assert result == []


# ---------------------------------------------------------------------------
# LocationsClient - optional parameters
# ---------------------------------------------------------------------------


def test_get_all_locations_with_filter_children(mocker, client):
    mocker.patch.object(
        client, "_request", return_value=[{"id": "1", "name": "Root Location"}]
    )
    result = client.locations.get_all_locations(filterChildren=True)
    assert len(result) == 1


def test_get_all_locations_empty(mocker, client):
    mocker.patch.object(client, "_request", return_value=[])
    result = client.locations.get_all_locations()
    assert result == []


def test_get_locations_tree_with_items(mocker, client):
    mocker.patch.object(
        client, "_request", return_value=[{"id": "1", "name": "Tree Node"}]
    )
    result = client.locations.get_locations_tree(withItems=True)
    assert len(result) == 1


def test_get_locations_tree_empty(mocker, client):
    mocker.patch.object(client, "_request", return_value=[])
    result = client.locations.get_locations_tree()
    assert result == []


# ---------------------------------------------------------------------------
# MaintenanceClient - optional parameters
# ---------------------------------------------------------------------------


def test_query_all_maintenance_with_status(mocker, client):
    mocker.patch.object(
        client, "_request", return_value=[{"id": "1", "name": "Scheduled"}]
    )
    result = client.maintenance.query_all_maintenance(
        status=MaintenanceFilterStatus.MaintenanceFilterStatusScheduled
    )
    assert len(result) == 1


def test_query_all_maintenance_completed(mocker, client):
    mocker.patch.object(
        client, "_request", return_value=[{"id": "2", "name": "Done"}]
    )
    result = client.maintenance.query_all_maintenance(
        status=MaintenanceFilterStatus.MaintenanceFilterStatusCompleted
    )
    assert result[0].name == "Done"


def test_query_all_maintenance_empty(mocker, client):
    mocker.patch.object(client, "_request", return_value=[])
    result = client.maintenance.query_all_maintenance()
    assert result == []


# ---------------------------------------------------------------------------
# LabelMakerClient - optional print parameter
# ---------------------------------------------------------------------------


def test_get_asset_label_with_print(mocker, client):
    mocker.patch.object(client, "_request", return_value="<svg>label</svg>")
    result = client.labelmaker.get_asset_label("1", print=True)
    assert result == "<svg>label</svg>"


def test_get_item_label_with_print(mocker, client):
    mocker.patch.object(client, "_request", return_value="<svg>label</svg>")
    result = client.labelmaker.get_item_label("1", print=True)
    assert result == "<svg>label</svg>"


def test_get_location_label_with_print(mocker, client):
    mocker.patch.object(client, "_request", return_value="<svg>label</svg>")
    result = client.labelmaker.get_location_label("1", print=True)
    assert result == "<svg>label</svg>"


# ---------------------------------------------------------------------------
# ProductsClient - optional data parameter
# ---------------------------------------------------------------------------


def test_search_ean_from_barcode_no_data(mocker, client):
    mocker.patch.object(client, "_request", return_value=[])
    result = client.products.search_ean_from_barcode()
    assert result == []


def test_create_qr_code_no_data(mocker, client):
    mocker.patch.object(client, "_request", return_value="qr_data")
    result = client.products.create_qr_code()
    assert result == "qr_data"


def test_search_ean_from_barcode_multiple(mocker, client):
    mocker.patch.object(
        client,
        "_request",
        return_value=[{"barcode": "123"}, {"barcode": "456"}],
    )
    result = client.products.search_ean_from_barcode("123")
    assert len(result) == 2


# ---------------------------------------------------------------------------
# NotifiersClient - empty list
# ---------------------------------------------------------------------------


def test_get_notifiers_empty(mocker, client):
    mocker.patch.object(client, "_request", return_value=[])
    result = client.notifiers.get_notifiers()
    assert result == []


# ---------------------------------------------------------------------------
# LabelsClient - empty list
# ---------------------------------------------------------------------------


def test_get_all_labels_empty(mocker, client):
    mocker.patch.object(client, "_request", return_value=[])
    result = client.labels.get_all_labels()
    assert result == []


# ---------------------------------------------------------------------------
# AssetsClient - with items
# ---------------------------------------------------------------------------


def test_get_item_by_asset_id_with_items(mocker, client):
    mocker.patch.object(
        client,
        "_request",
        return_value={
            "items": [{"id": "1", "name": "Found Item"}],
            "page": 1,
            "pageSize": 10,
            "total": 1,
        },
    )
    result = client.assets.get_item_by_asset_id("000-001")
    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].name == "Found Item"
