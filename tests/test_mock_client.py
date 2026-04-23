import os
import pytest
from homebox.client import HomeboxClient


def test_init_with_explicit_base_url():
    client = HomeboxClient(base_url="http://localhost:8080")
    assert client.base_url == "http://localhost:8080"
    assert client.token is None


def test_init_with_explicit_token():
    client = HomeboxClient(base_url="http://localhost:8080", token="mytoken")
    assert client.token == "mytoken"
    assert client.headers["Authorization"] == "Bearer mytoken"


def test_init_base_url_from_env(monkeypatch):
    monkeypatch.setenv("HOMEBOX_URL", "http://env-host:8080")
    monkeypatch.delenv("HOMEBOX_TOKEN", raising=False)
    client = HomeboxClient()
    assert client.base_url == "http://env-host:8080"
    assert client.token is None


def test_init_token_from_env(monkeypatch):
    monkeypatch.setenv("HOMEBOX_URL", "http://env-host:8080")
    monkeypatch.setenv("HOMEBOX_TOKEN", "env-token")
    client = HomeboxClient()
    assert client.token == "env-token"
    assert client.headers["Authorization"] == "Bearer env-token"


def test_explicit_base_url_overrides_env(monkeypatch):
    monkeypatch.setenv("HOMEBOX_URL", "http://env-host:8080")
    client = HomeboxClient(base_url="http://explicit-host:9090")
    assert client.base_url == "http://explicit-host:9090"


def test_explicit_token_overrides_env(monkeypatch):
    monkeypatch.setenv("HOMEBOX_URL", "http://env-host:8080")
    monkeypatch.setenv("HOMEBOX_TOKEN", "env-token")
    client = HomeboxClient(token="explicit-token")
    assert client.token == "explicit-token"


def test_missing_base_url_raises(monkeypatch):
    monkeypatch.delenv("HOMEBOX_URL", raising=False)
    with pytest.raises(ValueError, match="base_url"):
        HomeboxClient()
