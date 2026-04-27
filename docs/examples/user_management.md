# User Management

This example demonstrates how to create a group invitation token and use it to register a new user account in Homebox.

## What it demonstrates

- Authenticating as an admin user
- Creating a one-time group invitation with `client.groups.create_group_invitation()`
- Registering a new user account with `client.users.register_new_user()`

## Setup

Copy `examples/.env.sample` to `examples/.env` and set:

```
HOMEBOX_URL=https://your-homebox-instance/api
HOMEBOX_USERNAME=admin@example.com
HOMEBOX_PASSWORD=yourpassword
```

The authenticated user must have permissions to create group invitations.

Then run:

```bash
python examples/user_management.py
```

## Source code

```python title="examples/user_management.py"
--8<-- "examples/user_management.py"
```
