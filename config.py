import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", 0))
    TELEGRAM_PROXY: str = os.getenv("TELEGRAM_PROXY", "")

    YOOKASSA_SHOP_ID: str = os.getenv("YOOKASSA_SHOP_ID")
    YOOKASSA_SECRET_KEY: str = os.getenv("YOOKASSA_SECRET_KEY")
    YOOKASSA_RETURN_URL: str = os.getenv("YOOKASSA_RETURN_URL", "https://t.me/bot")
    PAYMENT_PRICE: float = float(os.getenv("PAYMENT_PRICE", 350))

    AWG_URL: str = os.getenv("AWG_URL", "http://127.0.0.1:51821")
    AWG_PASSWORD: str = os.getenv("AWG_PASSWORD")
    AWG_SERVER_IP: str = os.getenv("AWG_SERVER_IP")

    SUBSCRIPTION_DAYS: int = int(os.getenv("SUBSCRIPTION_DAYS", 30))
    REMINDER_DAYS_BEFORE: int = int(os.getenv("REMINDER_DAYS_BEFORE", 3))
    DB_PATH: str = os.getenv("DB_PATH", "/opt/vpn-shop-bot/data/vpn_bot.db")


cfg = Config()