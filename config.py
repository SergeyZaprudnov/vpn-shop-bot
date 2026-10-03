import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", 0))
    YOOKASSA_SHOP_ID: str = os.getenv("YOOKASSA_SHOP_ID")
    YOOKASSA_SECRET_KEY: str = os.getenv("YOOKASSA_SECRET_KEY")
    PAYMENT_PRICE: float = float(os.getenv("PAYMENT_PRICE", 100))
    AWG_URL: str = os.getenv("AWG_URL", "http://127.0.0.1:51821")
    AWG_PASSWORD: str = os.getenv("AWG_PASSWORD")
    AWG_SERVER_IP: str = os.getenv("AWG_SERVER_IP")
    SUBSCRIPTION_DAYS: int = 30
    REMINDER_DAYS_BEFORE: int = 3
    DB_PATH: str = os.getenv("DB_PATH", "/app/data/vpn_bot.db")


cfg = Config()