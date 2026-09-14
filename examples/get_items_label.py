"""Example script that creates labels for item-like Homebox entities.

The script selects a populated location-like entity, gets its child entities,
and creates a label for each non-location child.
Labels are saved as png files in the current directory.

In order to run this script, you need to have the following environment variables set:
- HOMEBOX_URL: the URL of your Homebox instance (e.g. http://localhost
- HOMEBOX_USERNAME: the username of a user with permissions to create locations and items
- HOMEBOX_PASSWORD: the password of that user

You can use the .env.sample file in the examples directory as a template for your .env file.
"""

from __future__ import annotations

import os
from pathlib import Path

from _v26 import get_location_entities, require_id

from homebox import HomeboxClient


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


def _safe_name(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_")
    return cleaned or "item"


def main() -> None:
    _load_dotenv()

    client = _build_client()

    locations = get_location_entities(client)
    if not locations:
        print("No locations found. Create at least one location with items first.")
        return
    print(f"Found {len(locations)} location(s). Looking for items in these locations...")
    for location in locations:
        if (location.itemCount or 0) > 0:
            break
    else:
        print("No locations with items found. Create at least one location with items first.")
        return

    print(f"Using location: {location.name} ({location.id})")

    location_id = require_id(location.id, resource="Location entity")
    page = client.entities.query_all_entities(parentIds=[location_id], page=1, pageSize=200)
    items = [
        entity for entity in page.items or [] if entity.entityType is None or entity.entityType.isLocation is not True
    ]
    if not items:
        print("No items found in this location.")
        return

    saved = 0
    for item in items:
        if not item.id:
            continue
        label_data = client.labelmaker.get_item_label(item.id, print=False)
        file_name = f"{_safe_name(item.name or item.id)}_{item.id[:8]}_label.png"
        output = Path.cwd() / file_name
        output.write_bytes(label_data)
        print(f"Saved label for '{item.name}' to {output}")
        saved += 1

    print(f"Generated {saved} label file(s)")


if __name__ == "__main__":
    main()
