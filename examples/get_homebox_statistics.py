"""Example script that shows how to retrieve various statistics from Homebox.

Script prints out  the statistics to the console.

In order to run this script, you need to have the following environment variables set:
- HOMEBOX_URL: the URL of your Homebox instance (e.g. http://localhost
- HOMEBOX_USERNAME: the username of a user with permissions to create locations and items
- HOMEBOX_PASSWORD: the password of that user

You can use the .env.sample file in the examples directory as a template for your .env file.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

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


def main() -> None:
    _load_dotenv()
    client = _build_client()

    app = client.application_info()
    currency = None

    # The currency endpoint is currently broken, raises  404 error
    # currency = client.currency()

    group_stats = client.groups.get_group_statistics()
    tag_stats = []
    # The tag statistics endpoint is broken, returns None
    # tag_stats = client.groups.get_tag_statistics()

    location_stats = client.groups.get_location_statistics()

    end = datetime.now(UTC).date()
    start = end - timedelta(days=30)
    purchase_stats = client.groups.get_purchase_price_statistics(start=start.isoformat(), end=end.isoformat())

    print("=== Homebox Application ===")
    print(f"Title: {app.title}")
    print(f"Version: {app.build.version if app.build else 'n/a'}")
    print(f"Health: {'ok' if app.health else 'not healthy'}")
    if currency:
        print(f"Currency: {currency.code} ({currency.symbol})")

    print("\n=== Group Totals ===")
    print(f"Items: {group_stats.totalItems}")
    print(f"Locations: {group_stats.totalLocations}")
    print(f"Labels: {group_stats.totalLabels}")
    print(f"Users: {group_stats.totalUsers}")
    print(f"Items with warranty: {group_stats.totalWithWarranty}")
    print(f"Total item value: {group_stats.totalItemPrice}")

    print("\n=== Value by Tag ===")
    for stat in sorted(tag_stats, key=lambda x: x.total or 0, reverse=True):
        print(f"- {stat.name}: {stat.total}")

    print("\n=== Value by Location ===")
    for stat in sorted(location_stats, key=lambda x: x.total or 0, reverse=True):
        print(f"- {stat.name}: {stat.total}")

    print("\n=== Purchase Price (Last 30 Days) ===")
    print(f"Value at start: {purchase_stats.valueAtStart}")
    print(f"Value at end: {purchase_stats.valueAtEnd}")
    for entry in purchase_stats.entries or []:
        print(f"- {entry.date}: {entry.value}")


if __name__ == "__main__":
    main()
