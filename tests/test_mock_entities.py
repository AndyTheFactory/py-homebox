import pytest

from homebox import models
from homebox.client import HomeboxClient


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_entity_crud_uses_v26_routes(mocker, client):
    request = mocker.patch.object(client, "_request", return_value={"id": "entity-1", "name": "Laptop"})

    created = client.entities.create_entity(
        models.EntityCreate(name="Laptop", entityTypeId="type-1", parentId="office", quantity=1.5)
    )
    fetched = client.entities.get_entity("entity-1")
    updated = client.entities.update_entity("entity-1", models.EntityUpdate(name="Laptop Pro"))
    patched = client.entities.patch_entity("entity-1", models.EntityPatch(parentId="desk"))
    client.entities.delete_entity("entity-1")

    assert created.name == fetched.name == updated.name == patched.name == "Laptop"
    assert request.call_args_list[0].args[:2] == ("post", "/v1/entities")
    assert request.call_args_list[0].kwargs["data"]["entityTypeId"] == "type-1"
    assert request.call_args_list[-1].args[:2] == ("delete", "/v1/entities/entity-1")


def test_query_entities_supports_v26_filters_and_total_price(mocker, client):
    request = mocker.patch.object(
        client,
        "_request",
        return_value={"items": [{"id": "1", "name": "Desk"}], "total": 1, "totalPrice": 25.5},
    )

    result = client.entities.query_all_entities(q="desk", page=2, pageSize=20, tags=["tag-1"], parentIds=["room-1"])

    assert result.totalPrice == 25.5
    assert result.items[0].name == "Desk"
    assert request.call_args.kwargs["params"] == {
        "q": "desk",
        "page": 2,
        "pageSize": 20,
        "tags": ["tag-1"],
        "parentIds": ["room-1"],
    }


def test_entity_field_values_passes_required_field_filter(mocker, client):
    request = mocker.patch.object(client, "_request", return_value={"data": ["Dell"]})
    assert client.entities.get_all_custom_field_values("Manufacturer") == ["Dell"]
    assert request.call_args.kwargs["params"] == {"field": "Manufacturer"}


def test_entity_attachments_and_external_links(mocker, client):
    request = mocker.patch.object(client, "_request", return_value={"id": "entity-1", "name": "Laptop"})

    client.entities.create_attachment("entity-1", b"photo", type="photo", primary=False, name="photo.jpg")
    client.entities.create_external_attachment(
        "entity-1",
        models.ExternalAttachmentRequest(
            attachment_type="manual", external_id="doc-1", source_type="drive", title="Manual"
        ),
    )

    upload = request.call_args_list[0]
    assert upload.args[:2] == ("post", "/v1/entities/entity-1/attachments")
    assert upload.kwargs["data"]["primary"] is False
    external = request.call_args_list[1]
    assert external.args[:2] == ("post", "/v1/entities/entity-1/attachments/external")
    assert external.kwargs["data"]["external_id"] == "doc-1"


def test_entity_types_crud(mocker, client):
    request = mocker.patch.object(
        client,
        "_request",
        side_effect=[
            {"data": [{"id": "type-1", "name": "Location", "isLocation": True}]},
            {"id": "type-2", "name": "Device"},
            {"id": "type-2", "name": "Equipment"},
            {},
        ],
    )

    assert client.entity_types.get_all_entity_types()[0].isLocation is True
    assert client.entity_types.create_entity_type(models.EntityTypeCreate(name="Device")).name == "Device"
    assert (
        client.entity_types.update_entity_type("type-2", models.EntityTypeUpdate(name="Equipment")).name == "Equipment"
    )
    client.entity_types.delete_entity_type("type-2")
    assert request.call_args_list[-1].args[:2] == ("delete", "/v1/entity-types/type-2")


def test_legacy_items_translate_to_v26_entity_contract(mocker, client):
    request = mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Laptop"})
    client.items.create_item(models.ItemCreate(name="Laptop", locationId="office", labelIds=["tag-1"]))
    assert request.call_args.args[:2] == ("post", "/v1/entities")
    assert request.call_args.kwargs["data"]["parentId"] == "office"
    assert request.call_args.kwargs["data"]["tagIds"] == ["tag-1"]
    assert "locationId" not in request.call_args.kwargs["data"]


def test_legacy_item_response_maps_v26_entity_names(mocker, client):
    mocker.patch.object(
        client,
        "_request",
        return_value={
            "id": "1",
            "name": "Laptop",
            "parent": {"id": "office", "name": "Office"},
            "purchaseDate": "2026-09-01",
            "soldDate": "2026-09-10",
            "syncChildEntityLocations": True,
        },
    )
    item = client.items.get_item("1")
    assert item.location.id == "office"
    assert item.purchaseTime == "2026-09-01"
    assert item.soldTime == "2026-09-10"
    assert item.syncChildItemsLocations is True
