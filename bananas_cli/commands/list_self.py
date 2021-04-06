import logging

from ..cli import (
    cli,
    pass_session,
)
from ..exceptions import Exit
from ..helpers import task

log = logging.getLogger(__name__)


@cli.command()
@pass_session
@task
async def list_self(session):
    status, data = await session.get("package/self")
    if status != 200:
        log.error(f"Server returned invalid status code {status}: {data}")
        raise Exit

    for package in data:
        print(f" - {package['name']}")
        for version in package["versions"]:
            print(f" |-- {version['version']} ({version['availability']})")
