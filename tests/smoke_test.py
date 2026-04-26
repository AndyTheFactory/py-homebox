"""Smoke tests for the homebox package.

These tests verify that the package installs correctly and that basic
objects can be instantiated without needing a live Homebox server.
They are run against the *built wheel* before every PyPI release.
"""

import homebox
from homebox import HomeboxClient, models


def test_version():
    """Package exposes a non-empty version string."""
    assert isinstance(homebox.__version__, str)
    assert len(homebox.__version__) > 0


def test_client_instantiation():
    """HomeboxClient can be instantiated with only a base URL."""
    client = HomeboxClient(base_url="http://localhost:8080")
    assert client.base_url == "http://localhost:8080"
    assert client.token is None


def test_client_with_token():
    """HomeboxClient stores the token and sets the Authorization header."""
    client = HomeboxClient(base_url="http://localhost:8080", token="test-token")
    assert client.token == "test-token"
    assert "Authorization" in client.headers
    assert client.headers["Authorization"] == "Bearer test-token"


def test_client_sub_clients_present():
    """HomeboxClient exposes all required sub-client attributes."""
    client = HomeboxClient(base_url="http://localhost:8080")
    assert client.actions is not None
    assert client.assets is not None
    assert client.groups is not None
    assert client.items is not None
    assert client.tags is not None
    assert client.labels is not None
    assert client.locations is not None
    assert client.maintenance is not None
    assert client.notifiers is not None
    assert client.users is not None
    assert client.reporting is not None
    assert client.labelmaker is not None
    assert client.products is not None


def test_models_importable():
    """Key model classes are importable from homebox.models."""
    assert models.ItemCreate is not None
    assert models.TagCreate is not None
    assert models.LabelCreate is not None
    assert models.LocationCreate is not None
    assert models.LoginForm is not None
    assert models.TokenResponse is not None
    assert models.ItemOut is not None
