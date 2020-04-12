import click
import logging

from ..cli import (
    cli,
    pass_session,
)
from ..enums import License
from ..exceptions import Exit
from ..helpers import task

log = logging.getLogger(__name__)


def show_validation_errors(data):
    log.error("Uploading failed with validation errors:")
    for error in data.get("errors", []):
        log.error(f" - {error}")


@cli.command()
@click.option("--version", help="Version of the package.", required=True)
@click.option("--name", help="Name of the package.")
@click.option("--description", help="Description of the package.")
@click.option("--url", help="URL of the package.")
@click.option("--license", help="License of the package.", type=click.Choice([license.value for license in License]))
@click.argument("files", nargs=-1, type=click.Path(exists=True, file_okay=True, dir_okay=False))
@pass_session
@task
async def upload(session, version, name, description, url, license, files):
    parts = files[0].split("/")[:-1]
    for filename in files:
        check_parts = filename.split("/")
        for i, part in enumerate(check_parts):
            if i >= len(parts):
                break

            if parts[i] != part:
                parts = parts[: i - 1]
                break

    starting_part = "/".join(parts) + "/"

    status, data = await session.post("/new-package", json={})
    if status != 200:
        log.error(f"Server returned invalid status code {status}: {data}")
        raise Exit

    upload_token = data["upload-token"]

    payload = {}

    if version:
        payload["version"] = version
    if name:
        payload["name"] = name
    if description:
        payload["description"] = description
    if url:
        payload["url"] = url
    if license:
        payload["license"] = license

    status, data = await session.put(f"/new-package/{upload_token}", json=payload)
    if status == 400:
        show_validation_errors(data)
        raise Exit
    if status != 204:
        log.error(f"Server returned invalid status code {status}: {data}")
        raise Exit

    for fullpath in files:
        filename = fullpath[len(starting_part) :]
        log.info(f"Uploading {filename} ...")
        session.tus_upload(upload_token, fullpath, filename)

    status, data = await session.post(f"/new-package/{upload_token}/publish", json={})
    if status == 400:
        show_validation_errors(data)
        raise Exit
    if status != 201:
        log.error(f"Server returned invalid status code {status}: {data}")
        raise Exit

    log.info("Uploaded successfully")
