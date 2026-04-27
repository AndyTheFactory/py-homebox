# py-homebox

A Python client library for the [Homebox](https://github.com/sysadminsmedia/homebox) REST API.
Homebox is a self-hosted home inventory management system that lets you track, manage, and organise your belongings.

**py-homebox** wraps every Homebox v1 endpoint in a clean, typed Python interface backed by [Pydantic](https://docs.pydantic.dev/) models, so you get auto-completion, validation, and inline documentation out of the box.

---

## Features

- Full coverage of the Homebox v1 API (items, labels, locations, maintenance, notifiers, groups, users, reporting, label-maker, products/barcodes)
- Pydantic v2 models for all request and response payloads
- Automatic Bearer-token injection after `login()`
- Environment-variable based configuration (no hard-coded credentials)

---

## Installation

Install from PyPI:

```bash
pip install homebox
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add homebox
```

---

## Compatibility

Version 0.1.0 is compatible with Homebox v0.21.0 API.

---

## Quick start

### Authenticate with environment variables

```python
import os
from homebox import HomeboxClient

os.environ["HOMEBOX_URL"] = "https://demo.homebox.software/api"
os.environ["HOMEBOX_TOKEN"] = "your-bearer-token"

client = HomeboxClient()
```

### Authenticate by passing arguments directly

```python
from homebox import HomeboxClient

client = HomeboxClient(
    base_url="https://demo.homebox.software/api",
    token="your-bearer-token",
)
```

### Authenticate with username and password

```python
from homebox import HomeboxClient

client = HomeboxClient(base_url="https://demo.homebox.software/api")
client.login("admin@admin.com", "admin")

# subsequent calls now carry the Bearer token automatically
```

---

## Environment variables

| Variable        | Required | Description                                                              |
|-----------------|----------|--------------------------------------------------------------------------|
| `HOMEBOX_URL`   | **Yes**  | Base URL of the Homebox API (e.g. `https://demo.homebox.software/api`) |
| `HOMEBOX_TOKEN` | No       | Pre-obtained Bearer token. Omit this and call `client.login()` instead. |

---

## Contributing

Pull requests are welcome.
Install the pre-commit hooks and linters to maintain code quality and consistency:

```bash
uv sync --group dev
pre-commit install
```
