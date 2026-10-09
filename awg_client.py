"""Асинхронный HTTP-клиент для управления клиентами в панели rylorin/amnezia-wg-easy."""
import aiohttp
import logging
from config import cfg

logger = logging.getLogger(__name__)


class AWGClient:
    """Обёртка над REST API панели rylorin с сессионной авторизацией."""

    def __init__(self):
        self.base = cfg.AWG_URL.rstrip("/")
        self.session: aiohttp.ClientSession | None = None
        self.password = cfg.AWG_PASSWORD
        self.logged_in = False

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
            self.logged_in = False
        return self.session

    async def _login(self) -> bool:
        """Логинится в панели, сохраняет cookie в сессии."""
        session = await self._get_session()
        try:
            async with session.post(
                f"{self.base}/api/session",
                json={"password": self.password}
            ) as resp:
                if resp.status == 200:
                    self.logged_in = True
                    logger.info("AWG login successful")
                    return True
                logger.error(f"AWG login failed: {resp.status} {await resp.text()}")
                return False
        except Exception as e:
            logger.exception(f"AWG login error: {e}")
            return False

    async def _request(self, method: str, path: str, **kwargs):
        session = await self._get_session()
        if not self.logged_in:
            if not await self._login():
                return None

        resp = await session.request(method, f"{self.base}{path}", **kwargs)

        if resp.status == 401:
            resp.release()
            if await self._login():
                resp = await session.request(method, f"{self.base}{path}", **kwargs)
        return resp

    async def create_client(self, name: str):
        resp = await self._request("POST", "/api/wireguard/client", json={"name": name})
        if resp and resp.status == 200:
            data = await resp.json()
            resp.release()
            return data
        return None

    async def get_client_config(self, client_id: str):
        resp = await self._request("GET", f"/api/wireguard/client/{client_id}/configuration")
        if resp and resp.status == 200:
            text = await resp.text()
            resp.release()
            return text
        return None

    async def get_clients(self) -> list:
        resp = await self._request("GET", "/api/wireguard/client")
        if resp and resp.status == 200:
            data = await resp.json()
            resp.release()
            return data
        return []

    async def disable_client(self, client_id: str) -> bool:
        resp = await self._request("POST", f"/api/wireguard/client/{client_id}/disable")
        ok = resp is not None and resp.status == 200
        if resp:
            resp.release()
        return ok

    async def enable_client(self, client_id: str) -> bool:
        resp = await self._request("POST", f"/api/wireguard/client/{client_id}/enable")
        ok = resp is not None and resp.status == 200
        if resp:
            resp.release()
        return ok

    async def delete_client(self, client_id: str) -> bool:
        resp = await self._request("DELETE", f"/api/wireguard/client/{client_id}")
        ok = resp is not None and resp.status == 200
        if resp:
            resp.release()
        return ok


awg = AWGClient()