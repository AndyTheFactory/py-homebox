import pytest

from homebox import models
from homebox.client import HomeboxClient


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_query_all_items(mocker, client: HomeboxClient):
    mocker.patch.object(
        client,
        "_request",
        return_value={"items": [], "page": 1, "pageSize": 10, "total": 0},
    )
    result = client.items.query_all_items()
    assert result.total == 0


def test_create_item(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Test Item"})
    result = client.items.create_item(models.ItemCreate(name="Test Item"))
    assert result.name == "Test Item"


def test_export_items(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_get", return_value="csv,data")
    result = client.items.export_items()
    assert result == "csv,data"


def test_get_all_custom_field_names(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"data": ["field1", "field2"]})
    result = client.items.get_all_custom_field_names()
    assert len(result) == 2


def test_get_all_custom_field_values(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"data": ["value1", "value2"]})
    result = client.items.get_all_custom_field_values()
    assert len(result) == 2


def test_import_items(mocker, client: HomeboxClient):
    mock_request = mocker.patch.object(client, "_request", return_value=None)
    client.items.import_items(b"csv,data")
    assert mock_request.call_args.kwargs["files"] == {"csv": ("items.csv", b"csv,data", "text/csv")}


def test_get_item(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Test Item"})
    result = client.items.get_item("1")
    assert result.name == "Test Item"


def test_update_item(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Updated Item"})
    result = client.items.update_item("1", models.ItemUpdate(name="Updated Item"))
    assert result.name == "Updated Item"


def test_delete_item(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=None)
    client.items.delete_item("1")


def test_patch_item(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Patched Item"})
    result = client.items.patch_item("1", models.ItemPatch(name="Patched Item"))
    assert result.name == "Patched Item"


def test_create_item_attachment(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Test Item"})
    result = client.items.create_item_attachment("1", b"file_content", name="test.txt")
    assert result.name == "Test Item"


def test_get_item_attachment(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_get", return_value="test_token")
    result = client.items.get_item_attachment("1", "1")
    assert result == "test_token"


def test_update_item_attachment(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Test Item"})
    result = client.items.update_item_attachment("1", "1", models.ItemAttachmentUpdate(title="New Title"))
    assert result.name == "Test Item"


def test_delete_item_attachment(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=None)
    client.items.delete_item_attachment("1", "1")


def test_duplicate_item(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "2", "name": "Test Item (copy)"})
    result = client.items.duplicate_item("1", models.DuplicateOptions(copyPrefix=" (copy)"))
    assert result.name == "Test Item (copy)"


def test_get_maintenance_log(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"data": [{"id": "1", "name": "Test Log"}]})
    result = client.items.get_maintenance_log("1")
    assert len(result) == 1
    assert result[0].name == "Test Log"


def test_create_maintenance_entry(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Test Entry"})
    result = client.items.create_maintenance_entry("1", models.MaintenanceEntryCreate(name="Test Entry"))
    assert result.name == "Test Entry"


def test_get_item_path(mocker, client: HomeboxClient):
    mocker.patch.object(
        client,
        "_request",
        return_value={"data": [{"id": "1", "name": "Test Item", "type": "item"}]},
    )
    result = client.items.get_item_path("1")
    assert len(result) == 1
    assert result[0].name == "Test Item"
