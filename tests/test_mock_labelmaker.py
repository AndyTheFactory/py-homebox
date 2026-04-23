import pytest

from homebox.client import HomeboxClient


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_get_asset_label(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value="label_data")
    result = client.labelmaker.get_asset_label("1")
    assert result == "label_data"


def test_get_item_label(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value="label_data")
    result = client.labelmaker.get_item_label("1")
    assert result == "label_data"


def test_get_location_label(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value="label_data")
    result = client.labelmaker.get_location_label("1")
    assert result == "label_data"
