import pytest

from homebox import models
from homebox.client import HomeboxClient


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_query_all_maintenance(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"data": [{"id": "1", "name": "Test Maintenance"}]})
    result = client.maintenance.query_all_maintenance()
    assert len(result) == 1
    assert result[0].name == "Test Maintenance"


def test_update_maintenance_entry(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Updated Maintenance"})
    result = client.maintenance.update_maintenance_entry("1", models.MaintenanceEntryUpdate(name="Updated Maintenance"))
    assert result.name == "Updated Maintenance"


def test_delete_maintenance_entry(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=None)
    client.maintenance.delete_maintenance_entry("1")
