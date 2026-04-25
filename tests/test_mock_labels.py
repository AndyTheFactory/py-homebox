import pytest

from homebox import models
from homebox.client import HomeboxClient


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_get_all_labels(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"data": [{"id": "1", "name": "Test Label"}]})
    result = client.labels.get_all_labels()
    assert len(result) == 1
    assert result[0].name == "Test Label"


def test_create_label(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Test Label"})
    result = client.labels.create_label(models.LabelCreate(name="Test Label"))
    assert result.name == "Test Label"


def test_get_label(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Test Label"})
    result = client.labels.get_label("1")
    assert result.name == "Test Label"


def test_update_label(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Updated Label"})
    result = client.labels.update_label("1", models.LabelOut(name="Updated Label"))
    assert result.name == "Updated Label"


def test_delete_label(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=None)
    client.labels.delete_label("1")
