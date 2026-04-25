"""Example script that shows how to manage users in Homebox.

Script demonstrates how to create, update, and delete users.

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

import requests

from homebox import HomeboxClient
from homebox.models import GroupInvitationCreate, UserRegistration


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
    admin_client = _build_client()
    ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")

    invitation_token: str | None = None
    try:
        invitation = admin_client.groups.create_group_invitation(
            GroupInvitationCreate(
                uses=1,
                expiresAt=(datetime.now(UTC) + timedelta(days=1)).isoformat(),
            )
        )
        invitation_token = invitation.token
        print(f"Created invitation token for registration: {invitation_token}")
    except requests.HTTPError as exc:
        print(f"Could not create invitation token ({exc}); attempting registration without token")

    email = f"example.user.{ts}@example.com"
    password = f"ExamplePass!{ts}"
    name = f"Example User {ts}"

    admin_client.users.register_new_user(
        UserRegistration(
            name=name,
            email=email,
            password=password,
            token=invitation_token,
        )
    )
    print(f"Created user: {email}")

    # user_client = HomeboxClient(base_url=admin_client.base_url)
    # user_client.login(email, password)

    # updated_name = f"{name} Updated"
    # updated_user = user_client.users.update_account(UserUpdate(name=updated_name))
    # print(f"Updated user profile name to: {updated_user.name}")

    # user_client.users.delete_account()
    # print("Deleted the created user account")


if __name__ == "__main__":
    main()
