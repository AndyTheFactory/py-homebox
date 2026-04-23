import pytest

from homebox.client import HomeboxClient


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_search_ean_from_barcode(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=[{"barcode": "123"}])
    result = client.products.search_ean_from_barcode("123")
    assert len(result) == 1
    assert result[0].barcode == "123"


def test_create_qr_code(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value="qr_code_data")
    result = client.products.create_qr_code("test")
    assert result == "qr_code_data"
