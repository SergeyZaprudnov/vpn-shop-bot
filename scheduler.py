"""Планировщик задач: напоминания об оплате и автоблокировка просроченных."""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from database import get_expiring_users, get_expired_users, deactivate_user
from awg_client import awg
from config import cfg

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


def setup_scheduler(bot: Bot):
    """Регистрирует cron-задачи: напоминание в 10:00, блокировка в 00:05."""

    async def remind():
        """Напоминает пользователям за N дней до окончания подписки."""
        users = await get_expiring_users(cfg.REMINDER_DAYS_BEFORE)
        for u in users:
            try:
                await bot.send_message(
                    u["user_id"],
                    f"⏰ Подписка истекает через {cfg.REMINDER_DAYS_BEFORE} дней. Продлите!"
                )
            except Exception:
                pass

    async def block_expired():
        """Блокирует клиентов с истёкшей подпиской."""
        users = await get_expired_users()
        for u in users:
            if u["client_id"] and await awg.disable_client(u["client_id"]):
                await deactivate_user(u["user_id"])
                try:
                    await bot.send_message(
                        u["user_id"],
                        "🚫 Подписка истекла. Доступ приостановлен."
                    )
                except Exception:
                    pass

    scheduler.add_job(remind, "cron", hour=10, minute=0, id="remind")
    scheduler.add_job(block_expired, "cron", hour=0, minute=5, id="block")
    scheduler.start()