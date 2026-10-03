"""Создание платежей через ЮKassa (Касса)."""
import uuid
import logging
from yookassa import Configuration, Payment
from config import cfg

logger = logging.getLogger(__name__)
Configuration.account_id = cfg.YOOKASSA_SHOP_ID
Configuration.secret_key = cfg.YOOKASSA_SECRET_KEY


def create_payment(user_id: int) -> dict | None:
    """
    Создаёт платёж в ЮKassa и возвращает {payment_id, confirmation_url}.
    confirmation_url — ссылка на страницу оплаты, которую получает пользователь.
    """
    try:
        idempotence_key = str(uuid.uuid4())
        payment_data = {
            "amount": {
                "value": f"{cfg.PAYMENT_PRICE:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": cfg.YOOKASSA_RETURN_URL
            },
            "capture": True,
            "description": "VPN подписка на 1 месяц",
            "metadata": {"user_id": str(user_id)}
        }

        # Чеки по 54-ФЗ (для самозанятых и ИП)
        if cfg.YOOKASSA_ENABLE_RECEIPTS and cfg.YOOKASSA_INN:
            payment_data["receipt"] = {
                "customer": {"email": cfg.YOOKASSA_DEFAULT_RECEIPT_EMAIL},
                "items": [{
                    "description": "VPN подписка",
                    "quantity": "1.00",
                    "amount": {"value": f"{cfg.PAYMENT_PRICE:.2f}", "currency": "RUB"},
                    "vat_code": 1,  # 1 = НДС не облагается
                    "payment_subject": "service",
                    "payment_mode": "full_payment"
                }]
            }

        payment = Payment.create(payment_data, idempotence_key)
        return {
            "payment_id": payment.id,
            "confirmation_url": payment.confirmation.confirmation_url,
        }
    except Exception as e:
        logger.exception(f"YooKassa create error: {e}")
        return None


def check_payment(payment_id: str) -> str:
    """Проверяет статус платежа: pending / succeeded / canceled."""
    try:
        payment = Payment.find_one(payment_id)
        return payment.status
    except Exception as e:
        logger.exception(f"YooKassa check error: {e}")
        return "error"