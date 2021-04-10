import click
import logging

from aiohttp.client_exceptions import ClientConnectorError
from .authentication import authenticate
from .helpers import task
from .session import Session
from .exceptions import Exit

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
@click.option("--audience", help="Audience to use for authentication", default="github", show_default=False)
@click.option("--verbose", help="Enable verbose output for errors, showing tracebacks", is_flag=True)
@click.pass_context
@task
async def cli(ctx, api_url, tus_url, client_id, audience, verbose):
    """
    A CLI tool to list, upload, and otherwise modify BaNaNaS content.

    Every option can also be set via an environment variable prefixed with
    BANANAS_CLI_; for example:

    BANANAS_CLI_API_URL="http://localhost:8000" python -m bananas_cli
    """

    global session

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO
    )

    if not tus_url:
        tus_url = api_url

    session = Session(api_url, tus_url, verbose)
    ctx.obj = session

    await session.start()

    os_args = click.get_os_args()
    if "-h" in os_args or "--help" in os_args:
        return

    try:
        await authenticate(session, client_id, audience)
    except (ClientConnectorError, NameError) as e:
        if verbose:
            log.exception(e)
        else:
            log.error(e)
        raise Exit


@task
async def cli_exit():
    if session:
        await session.stop()
