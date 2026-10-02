import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    """Чтение данных из файла .env"""
    BOT_TOKEN: str = os.getenv('BOT_TOKEN')
    ADMIN_ID: int = int(os.getenv('ADMIN_ID', 0))
    YOOKASSA_SHOP_ID: str = os.getenv('YOOKASSA_SHOP_ID')
    YOOKASSA_SECRET_KEY: str = os.getenv('YOOKASSA_SECRET_KEY')
    PAYMENT_PRICE: float = float(os.getenv('PAYMENT_PRICE', 100))
    AWG_URL: str = os.getenv('AWG_URL', 'http//127.0.0.1:51821')
    AWG_PASSWORD: str = os.getenv('AWG_PASSWORD')
    AWG_SERVER_IP: str = os.getenv('AWG_SERVER_IP')
    REMINDER_DAYS_BEFORE: int = 3

cfg = Config()
