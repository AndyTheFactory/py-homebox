import pytest

from homebox import models
from homebox.client import HomeboxClient


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


def test_oidc_login(mocker, client: HomeboxClient):
    mock_response = mocker.MagicMock()
    mock_response.headers = {"Location": "https://idp.example.com/auth"}
    mock_response.raise_for_status.return_value = None
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    result = client.users.oidc_login()

    assert result == "https://idp.example.com/auth"
    assert mock_get.call_args.kwargs["allow_redirects"] is False


def test_oidc_callback(mocker, client: HomeboxClient):
    mock_response = mocker.MagicMock()
    mock_response.headers = {"Location": "http://localhost:3000/"}
    mock_response.raise_for_status.return_value = None
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    result = client.users.oidc_callback("code123", "state456")

    assert result == "http://localhost:3000/"
    assert mock_get.call_args.kwargs["params"] == {"code": "code123", "state": "state456"}


def test_register_new_user(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=None)
    client.users.register_new_user(models.UserRegistration(name="test", email="test@example.com", password="password"))


def test_get_user_self(mocker, client: HomeboxClient):
    mocker.patch.object(
        client,
        "_request",
        return_value={
            "item": {
                "id": "1",
                "name": "Test User",
                "oidcIssuer": "https://idp.example.com",
                "oidcSubject": "abc-subject",
            }
        },
    )
    result = client.users.get_user_self()
    assert result.name == "Test User"
    assert result.oidcIssuer == "https://idp.example.com"
    assert result.oidcSubject == "abc-subject"


def test_update_account(mocker, client: HomeboxClient):
    mocker.patch.object(
        client, "_request", return_value={"item": {"id": "1", "name": "Updated User", "email": "updated@example.com"}}
    )
    result = client.users.update_account(models.UserUpdate(name="Updated User", email="updated@example.com"))
    assert result.name == "Updated User"
    assert result.email == "updated@example.com"


def test_delete_account(mocker, client: HomeboxClient):
    mocker.patch.object(client, "_request", return_value=None)
    client.users.delete_account()
