"""Точка входа: Flask (вебхуки ЮKassa и Telegram) + aiogram-бот."""
import asyncio
import logging
import threading
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher
from aiogram.types import BufferedInputFile, Update
from aiogram.client.session.aiohttp import AiohttpSession

from config import cfg
from database import init_db, get_user, update_subscription, record_payment
from bot.handlers import router
from bot.admin_handlers import router as admin_router
from scheduler import setup_scheduler
from awg_client import awg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Прокси для Telegram (если задан в .env)
if cfg.TELEGRAM_PROXY:
    session = AiohttpSession(proxy=cfg.TELEGRAM_PROXY)
    bot = Bot(token=cfg.BOT_TOKEN, session=session)
    logger.info(f"Telegram proxy enabled: {cfg.TELEGRAM_PROXY}")
else:
    bot = Bot(token=cfg.BOT_TOKEN)

dp = Dispatcher()
dp.include_router(router)
dp.include_router(admin_router)

loop = None


@app.route("/yookassa/webhook", methods=["POST"])
def yookassa_webhook():
    """Принимает уведомления от ЮKassa об успешной оплате."""
    logger.info(f"!!! Webhook received: {request.json}")

    event = request.json
    if event.get("event") == "payment.succeeded":
        try:
            user_id = int(event["object"]["metadata"]["user_id"])
            payment_id = event["object"]["id"]
            logger.info(f"Payment succeeded: user_id={user_id}, payment_id={payment_id}")

            asyncio.run_coroutine_threadsafe(
                process_payment(user_id, payment_id),
                loop
            )
        except Exception as e:
            logger.exception(f"Webhook processing error: {e}")

    return jsonify({"status": "ok"}), 200


@app.route("/telegram/webhook", methods=["POST"])
def telegram_webhook():
    """Вебхук от Telegram: принимает обновления от бота."""
    update = Update.model_validate(request.json, context={"bot": bot})
    asyncio.run_coroutine_threadsafe(dp.feed_update(bot, update), loop)
    return jsonify({"status": "ok"}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


async def process_payment(user_id: int, payment_id: str):
    """Создаёт клиента, читает конфиг, отправляет с retry."""
    client_name = f"user_{user_id}"
    logger.info(f"Processing payment for {client_name}")

    created = await awg.create_client(client_name)
    if not created:
        logger.error(f"Failed to create AWG client for {user_id}")
        return

    config_text = await awg.get_client_config(client_name)
    if not config_text:
        logger.error(f"Failed to read config for {client_name}")
        return

    await update_subscription(user_id, client_name, client_name, cfg.SUBSCRIPTION_DAYS)
    await record_payment(user_id, cfg.PAYMENT_PRICE, payment_id)

    # Retry отправки в Telegram (5 попыток с задержкой)
    for attempt in range(5):
        try:
            await bot.send_document(
                user_id,
                document=BufferedInputFile(
                    config_text.encode(),
                    filename=f"{client_name}.conf"
                ),
                caption="✅ VPN активен! Импортируйте файл в приложение AmneziaWG."
            )
            logger.info(f"Config sent to {user_id} (attempt {attempt+1})")
            return
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed: {e}")
            await asyncio.sleep(10)

    logger.error(f"Failed to send config to {user_id} after 5 attempts")


async def run_bot():
    """Инициализирует БД, планировщик и polling."""
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