import pytest

from homebox import models
from homebox.client import HomeboxClient


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_get_all_templates(mocker, client: HomeboxClient):
    mocker.patch.object(
        client,
        "_request",
        return_value={"data": [{"id": "tmpl-1", "name": "Laptop", "description": "Template"}]},
    )
    result = client.templates.get_all_templates()
    assert len(result) == 1
    assert result[0].id == "tmpl-1"


def test_create_template(mocker, client: HomeboxClient):
    mock_request = mocker.patch.object(client, "_request", return_value={"id": "tmpl-1", "name": "Laptop"})
    result = client.templates.create_template(models.ItemTemplateCreate(name="Laptop", defaultLabelIds=["tag-1"]))
    assert result.id == "tmpl-1"
    assert mock_request.call_args.kwargs["data"]["defaultTagIds"] == ["tag-1"]


def test_get_template(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "tmpl-1", "name": "Laptop"})
    result = client.templates.get_template("tmpl-1")
    assert result.name == "Laptop"


def test_update_template(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "tmpl-1", "name": "Updated"})
    result = client.templates.update_template("tmpl-1", models.ItemTemplateUpdate(name="Updated"))
    assert result.name == "Updated"


def test_delete_template(mocker, client: HomeboxClient):
    mock_request = mocker.patch.object(client, "_request", return_value={})
    client.templates.delete_template("tmpl-1")
    assert mock_request.call_args.args[0] == "delete"
    assert mock_request.call_args.args[1] == "/v1/templates/tmpl-1"


def test_create_item_from_template(mocker, client: HomeboxClient):
    mock_request = mocker.patch.object(client, "_request", return_value={"id": "item-1", "name": "Created"})
    result = client.templates.create_item_from_template(
        "tmpl-1",
        models.ItemTemplateCreateItemRequest(name="Created", locationId="loc-1", labelIds=["tag-1"]),
    )
    assert result.id == "item-1"
    assert mock_request.call_args.kwargs["data"]["tagIds"] == ["tag-1"]
