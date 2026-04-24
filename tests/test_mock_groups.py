import pytest

from homebox import models
from homebox.client import HomeboxClient


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_get_group(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Test Group"})
    result = client.groups.get_group()
    assert result.name == "Test Group"


def test_update_group(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Updated Group"})
    result = client.groups.update_group(models.GroupUpdate(name="Updated Group"))
    assert result.name == "Updated Group"


def test_create_group_invitation(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"token": "test_token"})
    result = client.groups.create_group_invitation(models.GroupInvitationCreate(uses=1))
    assert result.token == "test_token"


def test_get_group_statistics(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"totalItems": 10})
    result = client.groups.get_group_statistics()
    assert result.totalItems == 10


def test_get_label_statistics(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=[{"id": "1", "name": "Test Label", "total": 5}])
    result = client.groups.get_label_statistics()
    assert len(result) == 1
    assert result[0].name == "Test Label"


def test_get_location_statistics(mocker, client: HomeboxClient):
    mocker.patch.object(
        client,
        "_request",
        return_value=[{"id": "1", "name": "Test Location", "total": 5}],
    )
    result = client.groups.get_location_statistics()
    assert len(result) == 1
    assert result[0].name == "Test Location"


def test_get_purchase_price_statistics(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"valueAtStart": 100, "valueAtEnd": 200})
    result = client.groups.get_purchase_price_statistics()
    assert result.valueAtStart == 100
