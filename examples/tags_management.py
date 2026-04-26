"""Example script that shows how to create tags, add tags to items, and remove tags from items.

The script will create a new product and a series of new tags.
Then it will add the tags to the item, list the item tags.
Afterwards it will remove two of the tags, and list the item tags again.
Then it will update one of the tags, list the item tags again, and finally it will delete all the created tags.

In the end it will delete the created item.

In order to run this script, you need to have the following environment variables set:
- HOMEBOX_URL: the URL of your Homebox instance (e.g. http://localhost/api)
- HOMEBOX_USERNAME: the username of a user with permissions to create locations and items
- HOMEBOX_PASSWORD: the password of that user

You can use the .env.sample file in the examples directory as a template for your .env file.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from homebox import HomeboxClient
from homebox.models import ItemCreate, ItemPatch, LocationCreate, TagCreate


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


def _print_item_tags(client: HomeboxClient, item_id: str, title: str) -> None:
    item = client.items.get_item(item_id)
    tags = item.tags or []
    print(f"{title} ({len(tags)}):")
    for tag in tags:
        print(f"- {tag.name} ({tag.id})")


def main() -> None:
    _load_dotenv()
    client = _build_client()
    ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")

    created_location_id: str | None = None
    created_item_id: str | None = None
    created_tag_ids: list[str] = []

    try:
        location = client.locations.create_location(
            LocationCreate(
                name=f"Tag Demo Shelf {ts}",
                description="Location used by tags_management.py",
            )
        )
        created_location_id = location.id

        item = client.items.create_item(
            ItemCreate(
                name=f"Tag Demo Item {ts}",
                description="Item used by tags_management.py",
                locationId=location.id,
                quantity=1,
            )
        )
        created_item_id = item.id
        if not created_item_id:
            raise RuntimeError("Item was created but no item id was returned")
        print(f"Created item: {item.name} ({item.id})")

        seed_tags = [
            (f"Camera-{ts}", "#3b82f6"),
            (f"Office-{ts}", "#16a34a"),
            (f"Fragile-{ts}", "#f59e0b"),
            (f"Priority-{ts}", "#ef4444"),
        ]
        for name, color in seed_tags:
            created = client.tags.create_tag(TagCreate(name=name, color=color, description="Created by example script"))
            if created.id:
                created_tag_ids.append(created.id)
            print(f"Created tag: {created.name} ({created.id})")

        client.items.patch_item(created_item_id, ItemPatch(id=created_item_id, tagIds=created_tag_ids))
        _print_item_tags(client, created_item_id, "Item tags after adding all tags")

        remaining = created_tag_ids[2:]
        client.items.patch_item(created_item_id, ItemPatch(id=created_item_id, tagIds=remaining))
        _print_item_tags(client, created_item_id, "Item tags after removing first two tags")

        if remaining:
            tag_to_update = client.tags.get_tag(remaining[0])
            tag_to_update.name = f"Updated-{tag_to_update.name}"
            tag_to_update.description = "Updated by tags_management.py"
            tag_to_update.color = "#14b8a6"
            updated = client.tags.update_tag(remaining[0], tag_to_update)
            print(f"Updated tag: {updated.name} ({updated.id})")

        _print_item_tags(client, created_item_id, "Item tags after updating one tag")

    finally:
        for tag_id in created_tag_ids:
            client.tags.delete_tag(tag_id)
            print(f"Deleted tag: {tag_id}")

        if created_item_id:
            client.items.delete_item(created_item_id)
            print(f"Deleted item: {created_item_id}")

        if created_location_id:
            client.locations.delete_location(created_location_id)
            print(f"Deleted location: {created_location_id}")


if __name__ == "__main__":
    main()
