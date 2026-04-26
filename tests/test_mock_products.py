import pytest

from homebox.client import HomeboxClient


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_search_ean_from_barcode(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"data": [{"barcode": "123"}]})
    result = client.products.search_ean_from_barcode("123")
    assert len(result) == 1
    assert result[0].barcode == "123"


def test_create_qr_code(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_get", return_value="qr_code_data")
    result = client.products.create_qr_code("test")
    assert result == "qr_code_data"


def test_search_ean_from_barcode_accepts_float_item_quantity(mocker, client: HomeboxClient):
    mocker.patch.object(
        client,
        "_request",
        return_value={"data": [{"barcode": "123", "item": {"name": "Product", "quantity": 4.5}}]},
    )
    result = client.products.search_ean_from_barcode("123")
    assert result[0].item is not None
    assert result[0].item.quantity == 4.5
