# BaNaNaS CLI frontend

[![GitHub License](https://img.shields.io/github/license/OpenTTD/bananas-frontend-cli)](https://github.com/OpenTTD/bananas-frontend-cli/blob/main/LICENSE)
[![GitHub Tag](https://img.shields.io/github/v/tag/OpenTTD/bananas-frontend-cli?include_prereleases&label=stable)](https://github.com/OpenTTD/bananas-frontend-cli/releases)
[![GitHub commits since latest release](https://img.shields.io/github/commits-since/OpenTTD/bananas-frontend-cli/latest/main)](https://github.com/OpenTTD/bananas-frontend-cli/commits/main)

[![GitHub Workflow Status (Testing)](https://img.shields.io/github/actions/workflow/status/OpenTTD/bananas-frontend-cli/testing.yml?branch=main&label=main)](https://github.com/OpenTTD/bananas-frontend-cli/actions/workflows/testing.yml)

This is a CLI frontend for the OpenTTD's content service, called BaNaNaS.
It works together with [bananas-api](https://github.com/OpenTTD/bananas-api), which serves the HTTP API.

See [introduction.md](https://github.com/OpenTTD/bananas-api/tree/main/docs/introduction.md) for more documentation about the different BaNaNaS components and how they work together.

## Development

This CLI tool is written in Python 3.8 with aiohttp, and makes strong use of asyncio.

## Usage

To start it, you are advised to first create a virtualenv:

```bash
python3 -m venv .env
.env/bin/pip install -r requirements.txt
```

Next, check out the help.

```bash
.env/bin/python -m bananas_cli --help
```
