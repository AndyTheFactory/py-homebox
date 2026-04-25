import pytest

from homebox.client import HomeboxClient


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_export_bill_of_materials(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_get", return_value="csv,data")
    result = client.reporting.export_bill_of_materials()
    assert result == "csv,data"
