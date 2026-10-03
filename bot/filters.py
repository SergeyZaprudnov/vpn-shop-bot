from aiogram.filters import BaseFilter
from config import cfg


class IsAdmin(BaseFilter):
    async def __call__(self, event):
        return event.from_user.id == cfg.ADMIN_ID
