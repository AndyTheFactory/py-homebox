import os
import pytest
from homebox.client import HomeboxClient


@pytest.mark.real
@pytest.fixture
def client():
    base_url = os.environ.get("HOMEBOX_URL")
    if not base_url:
        pytest.skip("HOMEBOX_URL environment variable not set")
    return HomeboxClient(base_url=base_url)


@pytest.mark.real
def test_login(client: HomeboxClient):
    username = os.environ.get("HOMEBOX_USER")
    password = os.environ.get("HOMEBOX_PASSWORD")
    if not username or not password:
        pytest.skip("HOMEBOX_USER or HOMEBOX_PASSWORD environment variables not set")
    token_response = client.login(username, password)
    assert token_response.token
