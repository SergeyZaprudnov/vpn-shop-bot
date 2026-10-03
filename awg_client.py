import aiohttp
import logging
from config import cfg

logger = logging.getLogger(__name__)


class AWGClient:
    def __init__(self):
        self.base = cfg.AWG_URL.rstrip("/")
        self.session = None
        self.auth = aiohttp.BasicAuth("admin", cfg.AWG_PASSWORD)

    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(auth=self.auth)
        return self.session

    async def create_client(self, name: str):
        session = await self._get_session()
        try:
            async with session.post(
                f"{self.base}/api/wireguard/client",
                json={"name": name}
            ) as resp:
                if resp.status != 200:
                    logger.error(f"AWG create failed: {resp.status} {await resp.text()}")
                    return None
                return await resp.json()
        except Exception as e:
            logger.exception(f"AWG error: {e}")
            return None

    async def get_client_config(self, client_id: str):
        session = await self._get_session()
        try:
            async with session.get(
                f"{self.base}/api/wireguard/client/{client_id}/configuration"
            ) as resp:
                return await resp.text() if resp.status == 200 else None
        except Exception:
            return None

    async def disable_client(self, client_id: str) -> bool:
        session = await self._get_session()
        try:
            async with session.post(
                f"{self.base}/api/wireguard/client/{client_id}/disable"
            ) as resp:
                return resp.status == 200
        except Exception:
            return False

    async def enable_client(self, client_id: str) -> bool:
        session = await self._get_session()
        try:
            async with session.post(
                f"{self.base}/api/wireguard/client/{client_id}/enable"
            ) as resp:
                return resp.status == 200
        except Exception:
            return False

    async def delete_client(self, client_id: str) -> bool:
        session = await self._get_session()
        try:
            async with session.delete(
                f"{self.base}/api/wireguard/client/{client_id}"
            ) as resp:
                return resp.status == 200
        except Exception:
            return False


awg = AWGClient()