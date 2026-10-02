import uuid
import logging
from yookassa import Configuration, Payment
from config import cfg

logger = logging.getLogger(__name__)
Configuration.account_id = cfg.YOOKASSA_SHOP_ID
Configuration.secret_key = cfg.YOOKASSA_SECRET_KEY


def create_payment(user_id: int):
    try:
        idempotence_key = str(uuid.uuid4())
        payment = Payment.create({
            "amount": {"value": f"{cfg.PAYMENT_PRICE:.2f}", "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": "https//t/me/your_bot"},
            "capture": True,
            "description": "VPN подписка",
            "metadata": {"user_id": str(user_id)}
        }, idempotence_key)
        return {"payment_id": payment.id, "confirmation_url": payment.confirmation.confirmation_url}
    except Exception as e:
        logger.exception(f"Yookassa error: {e}")
        return None