"""Example script for creating an item from an existing Homebox template.

This example focuses on the `POST /v1/templates/{id}/create-item` flow.

In order to run this script, you need to have the following environment variables set:
- HOMEBOX_URL: the URL of your Homebox instance (e.g. http://localhost)
- HOMEBOX_USERNAME: the username of a user with permissions to create items
- HOMEBOX_PASSWORD: the password of that user
- HOMEBOX_TEMPLATE_ID: ID of an existing template to instantiate

You can use the .env.sample file in the examples directory as a template for your .env file.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from homebox import HomeboxClient
from homebox.models import ItemTemplateCreateItemRequest


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

    # Reuse an existing location as the create-item payload requires one.
    locations = client.locations.get_all_locations(filterChildren=False)
    if not locations:
        raise RuntimeError("No locations found. Create at least one location before running this example.")

    location_id = locations[0].id
    created_item_id: str | None = None

    try:
        created_item = client.templates.create_item_from_template(
            template_id,
            ItemTemplateCreateItemRequest(
                name=f"Template Item {ts}",
                locationId=location_id,
                quantity=1,
                description="Created from existing template via API",
            ),
        )
        created_item_id = created_item.id
        print(f"Created item from template {template_id}: {created_item.name} ({created_item.id})")

        # Show the ancestry path of the new item (location → item).
        path = client.items.get_item_path(created_item.id)
        print("Item path:")
        for node in path:
            print(f"  [{node.type}] {node.name} ({node.id})")

    finally:
        if created_item_id:
            client.items.delete_item(created_item_id)
            print(f"Deleted created item: {created_item_id}")


if __name__ == "__main__":
    main()
