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


def test_create_template_serializes_template_field_type(mocker, client: HomeboxClient):
    mock_request = mocker.patch.object(client, "_request", return_value={"id": "tmpl-1", "name": "Laptop"})
    client.templates.create_template(
        models.ItemTemplateCreate(
            name="Laptop",
            fields=[
                models.TemplateField(
                    name="Voltage",
                    type=models.TemplateFieldType.TypeNumber,
                    numberValue=230,
                )
            ],
        )
    )
    assert mock_request.call_args.kwargs["data"]["fields"][0]["type"] == "number"


def test_get_template(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "tmpl-1", "name": "Laptop"})
    result = client.templates.get_template("tmpl-1")
    assert result.name == "Laptop"


def test_get_template_wrapped_response(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"item": {"id": "tmpl-1", "name": "Laptop"}})
    result = client.templates.get_template("tmpl-1")
    assert result.id == "tmpl-1"
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


def test_create_item_from_template_wrapped_response(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"item": {"id": "item-1", "name": "Created"}})
    result = client.templates.create_item_from_template(
        "tmpl-1",
        models.ItemTemplateCreateItemRequest(name="Created", locationId="loc-1"),
    )
    assert result.id == "item-1"


def test_template_field_supports_v24_types_and_values():
    field = models.TemplateField(
        id="f1",
        name="Calibration Date",
        type=models.TemplateFieldType.TypeTime,
        timeValue="2026-01-01T00:00:00Z",
    )
    assert field.type == models.TemplateFieldType.TypeTime
    assert field.timeValue == "2026-01-01T00:00:00Z"


def test_template_default_quantity_accepts_float(mocker, client: HomeboxClient):
    mock_request = mocker.patch.object(client, "_request", return_value={"id": "tmpl-1", "name": "Laptop"})
    client.templates.create_template(models.ItemTemplateCreate(name="Laptop", defaultQuantity=1.5))
    assert mock_request.call_args.kwargs["data"]["defaultQuantity"] == 1.5


def test_create_item_from_template_accepts_float_quantity(mocker, client: HomeboxClient):
    mock_request = mocker.patch.object(
        client, "_request", return_value={"id": "item-1", "name": "Created", "quantity": 3.75}
    )
    result = client.templates.create_item_from_template(
        "tmpl-1",
        models.ItemTemplateCreateItemRequest(name="Created", locationId="loc-1", quantity=3.75),
    )
    assert result.quantity == 3.75
    assert mock_request.call_args.kwargs["data"]["quantity"] == 3.75
