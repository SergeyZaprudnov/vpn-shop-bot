"""Клиент для управления AmneziaWG через manage_amneziawg.sh (bivlked v5.37.1)."""
import asyncio
import json
import logging
import os

logger = logging.getLogger(__name__)

MANAGE_SCRIPT = "/root/awg/manage_amneziawg.sh"
CONF_DIR = "/root/awg"


class AWGClient:
    """Обёртка над manage_amneziawg.sh для вызова из бота."""

    async def _run(self, *args, timeout: int = 30) -> tuple[int, str, str]:
        """Запускает manage_amneziawg.sh с аргументами и флагом --yes."""
        cmd = ["bash", MANAGE_SCRIPT, *args, "--yes"]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            return proc.returncode, stdout.decode(), stderr.decode()
        except asyncio.TimeoutError:
            logger.error(f"manage script timeout: {args}")
            return 1, "", "timeout"

    def _extract_json(self, out: str):
        """Достаёт JSON из вывода скрипта (между INFO-логами)."""
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("[") or line.startswith("{"):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
        return None

    async def create_client(self, name: str) -> dict | None:
        """Создаёт клиента через manage_amneziawg.sh add."""
        rc, out, err = await self._run("add", name, "--psk")
        if rc != 0:
            logger.error(f"create_client failed: {err or out}")
            return None
        logger.info(f"Client '{name}' created")
        return {"name": name, "success": True}

    async def get_client_config(self, name: str) -> str | None:
        """Читает .conf файл клиента."""
        path = os.path.join(CONF_DIR, f"{name}.conf")
        try:
            with open(path, "r") as f:
                return f.read()
        except Exception as e:
            logger.exception(f"get_client_config error: {e}")
            return None

    async def get_clients(self) -> list:
        """Возвращает список клиентов (list --json)."""
        rc, out, err = await self._run("list", "--json")
        if rc != 0:
            logger.error(f"get_clients failed: {err or out}")
            return []
        data = self._extract_json(out)
        return data if isinstance(data, list) else []

    async def get_stats(self) -> list:
        """Возвращает статистику по клиентам (stats --json)."""
        rc, out, err = await self._run("stats", "--json")
        if rc != 0:
            return []
        data = self._extract_json(out)
        return data if isinstance(data, list) else []

    async def disable_client(self, name: str) -> bool:
        """В bivlked отключение = удаление."""
        rc, _, _ = await self._run("remove", name)
        return rc == 0

    async def enable_client(self, name: str) -> bool:
        """Пересоздаёт клиента (аналог включения)."""
        rc, _, _ = await self._run("regen", name)
        return rc == 0

    async def delete_client(self, name: str) -> bool:
        """Удаляет клиента."""
        rc, _, _ = await self._run("remove", name)
        return rc == 0


awg = AWGClient()