import pytest
from homebox.client import HomeboxClient
from homebox import models


@pytest.fixture
def client():
    return HomeboxClient(base_url="http://localhost:8080")


def test_change_password(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=None)
    client.users.change_password(models.ChangePassword(current="old", new="new"))


def test_user_logout(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=None)
    client.users.user_logout()


def test_user_token_refresh(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value={"token": "new_token"})
    result = client.users.user_token_refresh()
    assert result.token == "new_token"


def test_register_new_user(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=None)
    client.users.register_new_user(
        models.UserRegistration(
            name="test", email="test@example.com", password="password"
        )
    )


def test_get_user_self(mocker, client: HomeboxClient):
    mocker.patch.object(
        client, "_request", return_value={"item": {"id": "1", "name": "Test User"}}
    )
    result = client.users.get_user_self()
    assert result.name == "Test User"


def test_update_account(mocker, client: HomeboxClient):
    mocker.patch.object(
        client, "_request", return_value={"item": {"id": "1", "name": "Updated User"}}
    )
    result = client.users.update_account(models.UserUpdate(name="Updated User"))
    assert result.name == "Updated User"


def test_delete_account(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=None)
    client.users.delete_account()
