import pytest

from homebox import models
from homebox.client import HomeboxClient


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_group_export_lifecycle(mocker, client):
    request = mocker.patch.object(
        client,
        "_request",
        side_effect=[
            {"items": [{"id": "export-1", "kind": "export", "status": "completed"}]},
            {"id": "export-2", "status": "pending"},
            {"id": "export-2", "status": "completed"},
            {},
            {"id": "import-1", "kind": "import", "status": "pending"},
        ],
    )
    get = mocker.patch.object(client, "_get", return_value=b"zip")

    assert client.group_exports.list_exports().items[0].status == models.ExportStatus.Completed
    assert client.group_exports.start_export().status == models.ExportStatus.Pending
    assert client.group_exports.get_export("export-2").status == models.ExportStatus.Completed
    client.group_exports.delete_export("export-2")
    assert client.group_exports.download_export("export-1") == b"zip"
    imported = client.group_exports.import_collection(b"archive")

    assert get.call_args.args[0] == "/v1/group/exports/export-1/download"
    assert imported.kind == models.ExportKind.Import
    assert request.call_args.kwargs["files"]["file"][2] == "application/zip"


def test_password_reset_endpoints(mocker, client):
    request = mocker.patch.object(client, "_request", return_value={})
    client.users.forgot_password(models.ForgotPasswordRequest(email="user@example.com"))
    client.users.reset_password(models.ResetPasswordRequest(password="secret1", token="x" * 20))
    assert request.call_args_list[0].args[:2] == ("post", "/v1/users/forgot-password")
    assert request.call_args_list[1].args[:2] == ("post", "/v1/users/reset-password")


def test_api_key_endpoints(mocker, client):
    request = mocker.patch.object(
        client,
        "_request",
        side_effect=[
            {"data": [{"id": "key-1", "name": "Automation"}]},
            {"id": "key-2", "name": "CLI", "token": "secret"},
            {},
        ],
    )
    assert client.users.get_api_keys()[0].name == "Automation"
    created = client.users.create_api_key(models.APIKeyCreate(name="CLI"))
    assert created.token == "secret"
    client.users.delete_api_key("key-2")
    assert request.call_args_list[-1].args[:2] == ("delete", "/v1/users/self/api-keys/key-2")


def test_v26_tag_hierarchy_fields():
    tag = models.TagOut(
        id="parent",
        name="Hardware",
        icon="cpu",
        children=[{"id": "child", "name": "Laptops", "parentId": "parent"}],
    )
    assert tag.icon == "cpu"
    assert tag.children[0].parentId == "parent"


def test_template_create_entity_maps_legacy_location_to_parent(mocker, client):
    request = mocker.patch.object(client, "_request", return_value={"id": "entity-1", "name": "Laptop"})
    result = client.templates.create_entity_from_template(
        "template-1",
        models.EntityTemplateCreateItemRequest(name="Laptop", parentId="office", entityTypeId="device-type"),
    )
    assert result.id == "entity-1"
    assert request.call_args.kwargs["data"]["parentId"] == "office"
    assert request.call_args.kwargs["data"]["entityTypeId"] == "device-type"
