import pytest

from homebox import models
from homebox.client import HomeboxClient


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_get_group(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Test Group"})
    result = client.groups.get_group()
    assert result.name == "Test Group"


def test_update_group(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Updated Group"})
    result = client.groups.update_group(models.GroupUpdate(name="Updated Group"))
    assert result.name == "Updated Group"


def test_create_group_invitation(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"token": "test_token"})
    result = client.groups.create_group_invitation(models.GroupInvitationCreate(uses=1))
    assert result.token == "test_token"


def test_get_group_statistics(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"totalItems": 10, "totalTags": 3})
    result = client.groups.get_group_statistics()
    assert result.totalItems == 10
    assert result.totalLabels == 3


def test_create_group(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "New Group"})
    result = client.groups.create_group(models.CreateRequest(name="New Group"))
    assert result.name == "New Group"


def test_delete_group(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={})
    client.groups.delete_group()


def test_get_all_groups(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"data": [{"id": "1", "name": "Group A"}]})
    result = client.groups.get_all_groups()
    assert len(result) == 1
    assert result[0].name == "Group A"


def test_get_group_invitations(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"data": [{"id": "inv-1", "uses": 2}]})
    result = client.groups.get_group_invitations()
    assert len(result) == 1
    assert result[0].id == "inv-1"


def test_accept_group_invitation(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"id": "1", "name": "Joined"})
    result = client.groups.accept_group_invitation("token")
    assert result.name == "Joined"


def test_delete_group_invitation(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={})
    client.groups.delete_group_invitation("inv-1")


def test_get_group_members(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"data": [{"id": "u1", "name": "Alice"}]})
    result = client.groups.get_group_members()
    assert len(result) == 1
    assert result[0].name == "Alice"


def test_add_group_member(mocker, client: HomeboxClient):
    mock_request = mocker.patch.object(client, "_request", return_value={})
    client.groups.add_group_member(models.GroupMemberAdd(userId="u1"))
    assert mock_request.call_args.args[1] == "/v1/groups/members"


def test_remove_group_member(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={})
    client.groups.remove_group_member("u1")


def test_get_tag_statistics(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"data": [{"id": "1", "name": "Test Tag", "total": 5}]})
    result = client.groups.get_tag_statistics()
    assert len(result) == 1
    assert result[0].name == "Test Tag"


def test_get_label_statistics_alias(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"data": [{"id": "1", "name": "Test Tag", "total": 5}]})
    result = client.groups.get_label_statistics()
    assert len(result) == 1
    assert result[0].name == "Test Tag"


def test_get_location_statistics(mocker, client: HomeboxClient):
    mocker.patch.object(
        client,
        "_request",
        return_value={"data": [{"id": "1", "name": "Test Location", "total": 5}]},
    )
    result = client.groups.get_location_statistics()
    assert len(result) == 1
    assert result[0].name == "Test Location"


def test_get_purchase_price_statistics(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"valueAtStart": 100, "valueAtEnd": 200})
    result = client.groups.get_purchase_price_statistics()
    assert result.valueAtStart == 100
