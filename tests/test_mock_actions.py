import pytest

from homebox import models
from homebox.client import HomeboxClient


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_create_missing_thumbnails(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"completed": 5})
    result = client.actions.create_missing_thumbnails()
    assert result.completed == 5


def test_ensure_asset_ids(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"completed": 5})
    result = client.actions.ensure_asset_ids()
    assert result.completed == 5


def test_ensure_import_refs(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"completed": 5})
    result = client.actions.ensure_import_refs()
    assert result.completed == 5


def test_set_primary_photos(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"completed": 5})
    result = client.actions.set_primary_photos()
    assert result.completed == 5


def test_zero_out_time_fields(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"completed": 5})
    result = client.actions.zero_out_time_fields()
    assert result.completed == 5


def test_wipe_inventory(mocker, client: HomeboxClient):
    mock_request = mocker.patch.object(client, "_request", return_value={"completed": 42})
    result = client.actions.wipe_inventory(models.WipeInventoryOptions(wipeTags=True))
    assert result.completed == 42
    assert mock_request.call_args.args[1] == "/v1/actions/wipe-inventory"
    assert mock_request.call_args.kwargs["data"]["wipeTags"] is True
