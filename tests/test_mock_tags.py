import pytest

from homebox import models
from homebox.client import HomeboxClient


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_get_all_tags(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"data": [{"id": "1", "name": "Test Tag"}]})
    result = client.tags.get_all_tags()
    assert len(result) == 1
    assert result[0].name == "Test Tag"


def test_create_tag(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Test Tag"})
    result = client.tags.create_tag(models.TagCreate(name="Test Tag"))
    assert result.name == "Test Tag"


def test_get_tag(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Test Tag"})
    result = client.tags.get_tag("1")
    assert result.name == "Test Tag"


def test_update_tag(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Updated Tag"})
    result = client.tags.update_tag("1", models.TagOut(name="Updated Tag"))
    assert result.name == "Updated Tag"


def test_delete_tag(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=None)
    client.tags.delete_tag("1")
