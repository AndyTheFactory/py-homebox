import pytest

from homebox.client import HomeboxClient


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_get_item_by_asset_id(mocker, client: HomeboxClient):
    mocker.patch.object(
        client,
        "_request",
        return_value={"items": [], "page": 1, "pageSize": 10, "total": 0},
    )
    result = client.assets.get_item_by_asset_id("123")
    assert result.total == 0
