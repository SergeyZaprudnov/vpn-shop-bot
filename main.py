"""Точка входа: запускает Flask (вебхуки) и aiogram-бота параллельно."""
import asyncio
import logging
import threading
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher
from config import cfg
from database import init_db, get_user, update_subscription, record_payment
from bot.handlers import router
from bot.admin_handlers import router as admin_router
from scheduler import setup_scheduler
from awg_client import awg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
bot = Bot(token=cfg.BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)
dp.include_router(admin_router)


@app.route("/yookassa/webhook", methods=["POST"])
def yookassa_webhook():
    """Принимает уведомления от ЮKassa об успешной оплате."""
    event = request.json
    if event.get("event") == "payment.succeeded":
        user_id = int(event["object"]["metadata"]["user_id"])
        asyncio.run_coroutine_threadsafe(
            process_payment(user_id, event["object"]["id"]),
            loop
        )
    return jsonify({"status": "ok"}), 200


async def process_payment(user_id: int, payment_id: str):
    """Создаёт клиента, скачивает конфиг и отправляет пользователю."""
    client_name = f"user_{user_id}"
    client = await awg.create_client(client_name)
    if not client:
        return
    config_text = await awg.get_client_config(client["id"])
    if not config_text:
        return

    await update_subscription(user_id, client_name, client["id"], cfg.SUBSCRIPTION_DAYS)
    await record_payment(user_id, cfg.PAYMENT_PRICE, payment_id)

    try:
        await bot.send_document(
            user_id,
            document=("vpn.conf", config_text.encode()),
            caption="✅ VPN активен!"
        )
    except Exception:
        pass


async def run_bot():
    """Инициализирует БД, планировщик и запускает polling."""
    await init_db()
    setup_scheduler(bot)
    await dp.start_polling(bot)


def run_flask():
    """Запускает Flask в отдельном потоке."""
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    threading.Thread(target=run_flask, daemon=True).start()
    loop.run_until_complete(run_bot())