"""Фильтр для проверки, что команду отправил администратор."""
from aiogram.filters import BaseFilter
from config import cfg


class IsAdmin(BaseFilter):
    """Пропускает только пользователя с ADMIN_ID из .env."""

    async def __call__(self, event) -> bool:
        return event.from_user.id == cfg.ADMIN_ID