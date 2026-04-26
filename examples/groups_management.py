"""Example script on how to create groups, add users to groups, add, revoke invitations, and remove users from groups.

Script create a new group, create a new test-user, invites the user to the group.

Then it lists the group members, lists the group invitations.
It accepts the invitation for the test user, lists the group members again,
and finally removes the test user from the group.

In order to run this script, you need to have the following environment variables set:
- HOMEBOX_URL: the URL of your Homebox instance (e.g. http://localhost/api)
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
from homebox.models import CreateRequest, GroupInvitationCreate, UserRegistration


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


def _build_client(username: str | None = None, password: str | None = None) -> HomeboxClient:
    base_url = _require_env("HOMEBOX_URL")
    login_username = username or _require_env("HOMEBOX_USERNAME")
    login_password = password or _require_env("HOMEBOX_PASSWORD")

    client = HomeboxClient(base_url=base_url)
    client.login(login_username, login_password)
    return client


def _print_members(client: HomeboxClient, title: str) -> None:
    members = client.groups.get_group_members()
    print(f"{title} ({len(members)}):")
    for member in members:
        print(f"- {member.name} ({member.email}) id={member.id}, owner={member.isOwner}")


def _print_invitations(client: HomeboxClient, title: str) -> None:
    invitations = client.groups.get_group_invitations()
    print(f"{title} ({len(invitations)}):")
    for invitation in invitations:
        print(
            f"- id={invitation.id}, token={invitation.token}, uses={invitation.uses}, expiresAt={invitation.expiresAt}"
        )


def main() -> None:
    _load_dotenv()
    admin_client = _build_client()
    ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")

    invitation_id: str | None = None
    invitation_token: str | None = None
    user_client: HomeboxClient | None = None

    try:
        created_group = admin_client.groups.create_group(CreateRequest(name=f"Example Group {ts}"))
        print(f"Created group: {created_group.name} ({created_group.id})")

        invitation = admin_client.groups.create_group_invitation(
            GroupInvitationCreate(
                uses=3,
                expiresAt=(datetime.now(UTC) + timedelta(days=2)).isoformat(),
            )
        )
        invitation_id = invitation.id
        invitation_token = invitation.token
        print(f"Created invitation token: {invitation_token}")

        test_email = f"groups.example.{ts}@example.com"
        test_password = f"GroupsPass!{ts}"
        test_name = f"Groups User {ts}"

        try:
            admin_client.users.register_new_user(
                UserRegistration(
                    name=test_name,
                    email=test_email,
                    password=test_password,
                )
            )
            print(f"Created test user without token: {test_email}")
        except requests.HTTPError:
            if not invitation_token:
                raise
            admin_client.users.register_new_user(
                UserRegistration(
                    name=test_name,
                    email=test_email,
                    password=test_password,
                    token=invitation_token,
                )
            )
            print(f"Created test user with invitation token: {test_email}")

        _print_members(admin_client, "Group members before acceptance")
        _print_invitations(admin_client, "Group invitations before acceptance")

        user_client = _build_client(test_email, test_password)
        user_self = user_client.users.get_user_self()
        print(f"Logged in as test user: {user_self.name} ({user_self.id})")

        if invitation_id:
            try:
                accepted = user_client.groups.accept_group_invitation(invitation_id)
                print(f"Accepted invitation: joined group {accepted.name} ({accepted.id})")
            except requests.HTTPError as exc:
                print(f"Invitation acceptance failed or was not needed: {exc}")

        _print_members(admin_client, "Group members after acceptance")

        if user_self.id:
            try:
                admin_client.groups.remove_group_member(user_self.id)
                print(f"Removed test user from group: {user_self.id}")
            except requests.HTTPError as exc:
                print(f"Could not remove test user from group: {exc}")

        _print_members(admin_client, "Group members after removal")

    finally:
        if invitation_id:
            try:
                admin_client.groups.delete_group_invitation(invitation_id)
                print(f"Deleted invitation: {invitation_id}")
            except requests.HTTPError as exc:
                print(f"Could not delete invitation {invitation_id}: {exc}")

        if user_client is not None:
            try:
                user_client.users.delete_account()
                print("Deleted created test user account")
            except requests.HTTPError as exc:
                print(f"Could not delete created user account: {exc}")


if __name__ == "__main__":
    main()
