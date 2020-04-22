import click
import logging

from .authentication import authenticate
from .helpers import task
from .session import Session

log = logging.getLogger(__name__)
pass_session = click.make_pass_decorator(Session)
session = None

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--api-url", help="BaNaNaS API URL.", default="https://api.bananas.openttd.org", show_default=True, metavar="URL"
)
@click.option("--tus-url", help="BaNaNaS tus URL. (normally the same as --api-url)", metavar="URL")
@click.option("--client-id", help="Client-id to use for authentication", default="ape", show_default=True)
@click.pass_context
@task
async def cli(ctx, api_url, tus_url, client_id):
    """
    A CLI tool to list, upload, and otherwise modify BaNaNaS content.

    Every option can also be set via an environment variable prefixed with
    BANANAS_CLI_; for example:

    BANANAS_CLI_API_URL="http://localhost:8000" python -m bananas_clie
    """

    global session

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO
    )

    if not tus_url:
        tus_url = api_url

    session = Session(api_url, tus_url)
    ctx.obj = session

    await session.start()
    await authenticate(session, client_id)


@task
async def cli_exit():
    if session:
        await session.stop()
