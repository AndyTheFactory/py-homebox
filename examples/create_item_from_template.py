"""Example script for creating an entity from an existing Homebox template.

This example focuses on the `POST /v1/templates/{id}/create-item` flow.

In order to run this script, you need to have the following environment variables set:
- HOMEBOX_URL: the URL of your Homebox instance (e.g. http://localhost)
- HOMEBOX_USERNAME: the username of a user with permissions to create entities
- HOMEBOX_PASSWORD: the password of that user
- HOMEBOX_TEMPLATE_ID: ID of an existing template to instantiate

You can use the .env.sample file in the examples directory as a template for your .env file.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from _v26 import get_location_entities, require_entity_type, require_id

from homebox import HomeboxClient
from homebox.models import EntityTemplateCreateItemRequest


def _load_dotenv() -> None:
    dotenv_path = Path(__file__).parent / ".env"
    if not dotenv_path.is_file():
        return

    with dotenv_path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _build_client() -> HomeboxClient:
    base_url = _require_env("HOMEBOX_URL")
    username = _require_env("HOMEBOX_USERNAME")
    password = _require_env("HOMEBOX_PASSWORD")

    client = HomeboxClient(base_url=base_url)
    client.login(username, password)
    return client


def main() -> None:
    _load_dotenv()
    client = _build_client()

    template_id = _require_env("HOMEBOX_TEMPLATE_ID")
    ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")

    # Reuse an existing location-like entity as the template payload requires a parent.
    locations = get_location_entities(client)
    if not locations:
        raise RuntimeError("No locations found. Create at least one location before running this example.")

    location_id = require_id(locations[0].id, resource="Location entity")
    entity_type = require_entity_type(client, is_location=False)
    created_entity_id: str | None = None

    try:
        created_entity = client.templates.create_entity_from_template(
            template_id,
            EntityTemplateCreateItemRequest(
                name=f"Template Entity {ts}",
                parentId=location_id,
                entityTypeId=entity_type.id,
                quantity=1,
                description="Created from existing template via API",
            ),
        )
        created_entity_id = require_id(created_entity.id, resource="Template-created entity")
        print(f"Created entity from template {template_id}: {created_entity.name} ({created_entity.id})")

        # Show the ancestry path of the new entity (location → entity).
        path = client.entities.get_entity_path(created_entity_id)
        print("Entity path:")
        for node in path:
            node_type = node.type.value if node.type else "unknown"
            print(f"  [{node_type}] {node.name} ({node.id})")

    finally:
        if created_entity_id:
            client.entities.delete_entity(created_entity_id)
            print(f"Deleted created entity: {created_entity_id}")


if __name__ == "__main__":
    main()
