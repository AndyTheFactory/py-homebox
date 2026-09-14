"""Example script that shows how to create tags and assign them to entities.

The script creates an entity and a series of tags.
It assigns the tags to the entity and lists them.
Afterwards it will remove two of the tags, and list the item tags again.
Then it will update one of the tags, list the item tags again, and finally it will delete all the created tags.

In the end it deletes the created entities.

In order to run this script, you need to have the following environment variables set:
- HOMEBOX_URL: the URL of your Homebox instance (e.g. http://localhost/api)
- HOMEBOX_USERNAME: the username of a user with permissions to create entities
- HOMEBOX_PASSWORD: the password of that user

You can use the .env.sample file in the examples directory as a template for your .env file.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from _v26 import require_entity_type, require_id

from homebox import HomeboxClient
from homebox.models import EntityCreate, EntityPatch, TagCreate, TagUpdate


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


def _print_entity_tags(client: HomeboxClient, entity_id: str, title: str) -> None:
    entity = client.entities.get_entity(entity_id)
    tags = entity.tags or []
    print(f"{title} ({len(tags)}):")
    for tag in tags:
        print(f"- {tag.name} ({tag.id})")


def main() -> None:
    _load_dotenv()
    client = _build_client()
    ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    location_type = require_entity_type(client, is_location=True)
    item_type = require_entity_type(client, is_location=False)

    created_location_id: str | None = None
    created_item_id: str | None = None
    created_tag_ids: list[str] = []

    try:
        location = client.entities.create_entity(
            EntityCreate(
                name=f"Tag Demo Shelf {ts}",
                description="Location used by tags_management.py",
                entityTypeId=location_type.id,
            )
        )
        created_location_id = require_id(location.id, resource="Location entity")

        item = client.entities.create_entity(
            EntityCreate(
                name=f"Tag Demo Entity {ts}",
                description="Entity used by tags_management.py",
                entityTypeId=item_type.id,
                parentId=created_location_id,
                quantity=1,
            )
        )
        created_item_id = require_id(item.id, resource="Tagged entity")
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

        client.entities.patch_entity(created_item_id, EntityPatch(id=created_item_id, tagIds=created_tag_ids))
        _print_entity_tags(client, created_item_id, "Entity tags after adding all tags")

        remaining = created_tag_ids[2:]
        client.entities.patch_entity(created_item_id, EntityPatch(id=created_item_id, tagIds=remaining))
        _print_entity_tags(client, created_item_id, "Entity tags after removing first two tags")

        if remaining:
            current_tag = client.tags.get_tag(remaining[0])
            updated = client.tags.update_tag(
                remaining[0],
                TagUpdate(
                    id=current_tag.id,
                    name=f"Updated-{current_tag.name}",
                    description="Updated by tags_management.py",
                    color="#14b8a6",
                    icon=current_tag.icon,
                    parentId=current_tag.parentId,
                ),
            )
            print(f"Updated tag: {updated.name} ({updated.id})")

        _print_entity_tags(client, created_item_id, "Entity tags after updating one tag")

    finally:
        for tag_id in created_tag_ids:
            client.tags.delete_tag(tag_id)
            print(f"Deleted tag: {tag_id}")

        if created_item_id:
            client.entities.delete_entity(created_item_id)
            print(f"Deleted entity: {created_item_id}")

        if created_location_id:
            client.entities.delete_entity(created_location_id)
            print(f"Deleted location: {created_location_id}")


if __name__ == "__main__":
    main()
