import pytest

from homebox import models
from homebox.client import HomeboxClient


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_get_all_locations(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=[{"id": "1", "name": "Test Location"}])
    result = client.locations.get_all_locations()
    assert len(result) == 1
    assert result[0].name == "Test Location"


def test_create_location(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Test Location"})
    result = client.locations.create_location(models.LocationCreate(name="Test Location"))
    assert result.name == "Test Location"


def test_get_locations_tree(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=[{"id": "1", "name": "Test Location"}])
    result = client.locations.get_locations_tree()
    assert len(result) == 1
    assert result[0].name == "Test Location"


def test_get_location(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Test Location"})
    result = client.locations.get_location("1")
    assert result.name == "Test Location"


def test_update_location(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Updated Location"})
    result = client.locations.update_location("1", models.LocationUpdate(name="Updated Location"))
    assert result.name == "Updated Location"


def test_delete_location(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=None)
    client.locations.delete_location("1")
