import aiohttp
import logging

from tusclient.client import TusClient
from tusclient.exceptions import TusCommunicationError

from .exceptions import Exit

log = logging.getLogger(__name__)

UPLOAD_CHUNK_SIZE = 5 * 1024 * 1024


class Session:
    def __init__(self, api_url, tus_url):
        self.session = None
        self.api_url = api_url
        self.tus_url = tus_url

        self._headers = {}

    async def start(self):
        self.session = aiohttp.ClientSession()

    async def stop(self):
        await self.session.close()

    async def _read_response(self, response):
        if response.status in (200, 201, 400, 404):
            if response.content_type == "text/html":
                return 302, response.url
            data = await response.json()
        elif response.status in (301, 302):
            data = response.headers["Location"]
        else:
            data = None

        return response.status, data

    async def get(self, url):
        response = await self.session.get(f"{self.api_url}{url}", headers=self._headers, allow_redirects=False)
        return await self._read_response(response)

    async def post(self, url, json):
        response = await self.session.post(
            f"{self.api_url}{url}", json=json, headers=self._headers, allow_redirects=False
        )
        return await self._read_response(response)

    async def put(self, url, json):
        response = await self.session.put(
            f"{self.api_url}{url}", json=json, headers=self._headers, allow_redirects=False
        )
        return await self._read_response(response)

    def tus_upload(self, upload_token, fullpath, filename):
        tus = TusClient(f"{self.tus_url}/new-package/tus/")

        try:
            uploader = tus.uploader(
                fullpath, chunk_size=UPLOAD_CHUNK_SIZE, metadata={"filename": filename, "upload-token": upload_token}
            )
            uploader.upload()
        except TusCommunicationError:
            log.exception(f"Failed to upload file '{filename}'")
            raise Exit

    def set_header(self, header, value):
        self._headers[header] = value
