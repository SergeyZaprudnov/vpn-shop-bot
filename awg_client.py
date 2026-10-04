"""Асинхронный HTTP-клиент для управления клиентами в панели AmneziaWG Easy."""
import aiohttp
import logging
from config import cfg

logger = logging.getLogger(__name__)


class AWGClient:
    """Обёртка над REST API панели AmneziaWG Easy (порт 51821)."""

    def __init__(self):
        self.base = cfg.AWG_URL.rstrip("/")
        self.session = None
        self.auth = aiohttp.BasicAuth("admin", cfg.AWG_PASSWORD)

    async def _get_session(self):
        """Ленивая инициализация сессии aiohttp."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(auth=self.auth)
        return self.session

    async def create_client(self, name: str):
        """Создаёт нового клиента. Возвращает dict с id или None."""
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
        """Скачивает .conf файл клиента как текст."""
        session = await self._get_session()
        try:
            async with session.get(
                f"{self.base}/api/wireguard/client/{client_id}/configuration"
            ) as resp:
                return await resp.text() if resp.status == 200 else None
        except Exception:
            return None

    async def get_clients(self) -> list:
        """Возвращает список всех клиентов из панели AmneziaWG."""
        session = await self._get_session()
        try:
            async with session.get(
                f"{self.base}/api/wireguard/client"
            ) as resp:
                if resp.status != 200:
                    logger.error(f"AWG get_clients failed: {resp.status}")
                    return []
                return await resp.json()
        except Exception as e:
            logger.exception(f"AWG get_clients error: {e}")
            return []

    async def disable_client(self, client_id: str) -> bool:
        """Блокирует клиента (сохраняя ключи)."""
        session = await self._get_session()
        try:
            async with session.post(
                f"{self.base}/api/wireguard/client/{client_id}/disable"
            ) as resp:
                return resp.status == 200
        except Exception:
            return False

    async def enable_client(self, client_id: str) -> bool:
        """Разблокирует клиента."""
        session = await self._get_session()
        try:
            async with session.post(
                f"{self.base}/api/wireguard/client/{client_id}/enable"
            ) as resp:
                return resp.status == 200
        except Exception:
            return False

    async def delete_client(self, client_id: str) -> bool:
        """Удаляет клиента из панели."""
        session = await self._get_session()
        try:
            async with session.delete(
                f"{self.base}/api/wireguard/client/{client_id}"
            ) as resp:
                return resp.status == 200
        except Exception:
            return False


awg = AWGClient()