"""Точка входа: запускает Flask (вебхуки) и aiogram-бота параллельно."""
import asyncio
import logging
import threading
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher
from aiogram.types import BufferedInputFile

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

    # 1. Создаём клиента в панели
    created = await awg.create_client(client_name)
    if not created:
        logger.error(f"Failed to create AWG client for {user_id}")
        return

    # 2. Ищем его в списке
    clients = await awg.get_clients()
    client = next((c for c in clients if c.get("name") == client_name), None)
    if not client:
        logger.error(f"Client '{client_name}' not found after creation")
        return

    # 3. Извлекаем id
    client_id = (
        client.get("id")
        or client.get("_id")
        or client.get("clientId")
        or client.get("publicKey")
    )
    if not client_id:
        logger.error(f"Unknown client format: {client}")
        return

    # 4. Скачиваем конфиг
    config_text = await awg.get_client_config(client_id)
    if not config_text:
        logger.error(f"Failed to get config for {client_name}")
        return

    # 5. Сохраняем в БД
    await update_subscription(user_id, client_name, client_id, cfg.SUBSCRIPTION_DAYS)
    await record_payment(user_id, cfg.PAYMENT_PRICE, payment_id)

    # 6. Отправляем пользователю
    try:
        await bot.send_document(
            user_id,
            document=BufferedInputFile(
                config_text.encode(),
                filename="vpn.conf"
            ),
            caption="✅ VPN активен!"
        )
    except Exception as e:
        logger.exception(f"Failed to send config to {user_id}: {e}")


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