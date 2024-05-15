import asyncio
import base64
import click
import hashlib
import logging
import os
import secrets

from aiohttp import web
from aiohttp.web_log import AccessLogger

from .exceptions import Exit

log = logging.getLogger(__name__)


class NoAccessLogger(AccessLogger):
    def log(self, request, response, time):
        pass


class Authenticate:
    event = asyncio.Event()
    routes = web.RouteTableDef()
    code_verifier = None
    session = None
    token_filename = None
    success = False

    @staticmethod
    @routes.get("/")
    async def callback(request):
        try:
            code = request.query.get("code")
            status, data = await Authenticate.session.post(
                "/user/token",
                json={
                    "client_id": "ape",
                    "redirect_uri": "http://localhost:3977/",
                    "code_verifier": Authenticate.code_verifier,
                    "code": code,
                    "grant_type": "authorization_code",
                },
            )
            if status != 200:
                log.error(f"Server returned invalid status code {status}. Authentication failed.")
                return web.Response(text="Authentication failed because the OAuth Provider returned an error.")

            with open(Authenticate.token_filename, "w") as f:
                f.write(data["access_token"])
            Authenticate.session.set_header("Authorization", f"Bearer {data['access_token']}")

            Authenticate.success = True

            return web.Response(text="Authentication succeeded. You can now close your browser.")
        except Exception:
            log.exception("Internal error. Please report to the developers.")
            return web.Response(text="Authentication failed because there was an error in the application.")
        finally:
            Authenticate.session = None
            Authenticate.code_verifier = None
            Authenticate.event.set()

    @staticmethod
    async def wait_for_code():
        # Create a very small webserver
        webapp = web.Application()
        webapp.add_routes(Authenticate.routes)

        # Start the webapp, and wait for the code to be send back
        task = asyncio.create_task(
            web._run_app(webapp, host="127.0.0.1", port=3977, print=None, access_log_class=NoAccessLogger)
        )
        await Authenticate.event.wait()
        task.cancel()

        if not Authenticate.success:
            raise Exit


async def authenticate(session, client_id):
    config_folder = click.get_app_dir("bananas-cli")
    os.makedirs(config_folder, exist_ok=True)
    token_filename = config_folder + "/token"

    if os.path.exists(token_filename):
        with open(token_filename, "r") as f:
            bearer_token = f.read()

        session.set_header("Authorization", f"Bearer {bearer_token}")
        status, data = await session.get("user")
        if status == 200:
            return

    Authenticate.token_filename = token_filename
    Authenticate.session = session
    Authenticate.code_verifier = secrets.token_hex(32)

    digest = hashlib.sha256(Authenticate.code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")

    status, data = await session.get(
        "user/authorize?"
        "audience=github&"
        "redirect_uri=http%3A%2F%2Flocalhost%3A3977%2F&"
        "response_type=code&"
        f"client_id={client_id}&"
        f"code_challenge={code_challenge}&"
        "code_challenge_method=S256"
    )
    if status != 302:
        log.error(f"Server returned invalid status code {status}. Authentication failed. Error: {data}")
        raise Exit

    print("Please visit the following URL to authenticate:")
    print(f"  {data}")

    await Authenticate.wait_for_code()
