import pytest
from homebox.client import HomeboxClient
from homebox import models


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_get_notifiers(mocker, client: HomeboxClient):
    mocker.patch.object(
        client, "_request", return_value=[{"id": "1", "name": "Test Notifier"}]
    )
    result = client.notifiers.get_notifiers()
    assert len(result) == 1
    assert result[0].name == "Test Notifier"


def test_create_notifier(mocker, client: HomeboxClient):
    mocker.patch.object(
        client, "_request", return_value={"id": "1", "name": "Test Notifier"}
    )
    result = client.notifiers.create_notifier(
        models.NotifierCreate(name="Test Notifier", url="http://localhost")
    )
    assert result.name == "Test Notifier"


def test_test_notifier(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=None)
    client.notifiers.test_notifier("http://localhost")


def test_update_notifier(mocker, client: HomeboxClient):
    mocker.patch.object(
        client, "_request", return_value={"id": "1", "name": "Updated Notifier"}
    )
    result = client.notifiers.update_notifier(
        "1", models.NotifierUpdate(name="Updated Notifier")
    )
    assert result.name == "Updated Notifier"


def test_delete_notifier(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=None)
    client.notifiers.delete_notifier("1")
