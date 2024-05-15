import aiohttp
import logging
import urllib.parse

from tusclient.client import TusClient
from tusclient.exceptions import TusCommunicationError

from .exceptions import Exit

log = logging.getLogger(__name__)

UPLOAD_CHUNK_SIZE = 5 * 1024 * 1024


class Session:
    def __init__(self, api_url, tus_url):
        self.session = None
        self.api_url = f"{api_url}/"
        self.tus_url = f"{tus_url}/"

        self._headers = {}

    async def start(self):
        self.session = aiohttp.ClientSession()

    async def stop(self):
        await self.session.close()

    async def _read_response(self, response):
        if response.status in (200, 201, 400, 404):
            data = await response.json()
        elif response.status in (301, 302):
            data = response.headers["Location"]
        else:
            data = None

        return response.status, data

    async def get(self, url):
        full_url = urllib.parse.urljoin(self.api_url, url)
        response = await self.session.get(full_url, headers=self._headers, allow_redirects=False)
        return await self._read_response(response)

    async def post(self, url, json):
        full_url = urllib.parse.urljoin(self.api_url, url)
        response = await self.session.post(full_url, json=json, headers=self._headers, allow_redirects=False)
        return await self._read_response(response)

    async def put(self, url, json):
        full_url = urllib.parse.urljoin(self.api_url, url)
        response = await self.session.put(full_url, json=json, headers=self._headers, allow_redirects=False)
        return await self._read_response(response)

    def tus_upload(self, upload_token, fullpath, filename):
        full_url = urllib.parse.urljoin(self.tus_url, "new-package/tus/")
        tus = TusClient(full_url)

        try:
            uploader = tus.uploader(
                fullpath,
                chunk_size=UPLOAD_CHUNK_SIZE,
                metadata={"filename": filename, "upload-token": upload_token},
            )
            uploader.upload()
        except TusCommunicationError:
            log.exception(f"Failed to upload file '{filename}'")
            raise Exit

    def set_header(self, header, value):
        self._headers[header] = value
