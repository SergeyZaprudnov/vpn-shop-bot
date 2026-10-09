"""Обработчики команд и кнопок для обычных пользователей."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
import logging

from database import (
    add_user, get_user, update_subscription,
    set_last_message, get_last_message
)
from awg_client import awg
from payments import create_payment
from bot.keyboards import (
    main_menu, payment_keyboard, install_help_keyboard,
    admin_menu
)
from config import cfg

logger = logging.getLogger(__name__)
router = Router()


class BuyState(StatesGroup):
    waiting_for_name = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """При /start: админ видит админ-панель, пользователь — меню покупки."""
    name = message.from_user.first_name or "друг"

    if message.from_user.id == cfg.ADMIN_ID:
        await message.answer(
            f"👋 Привет, <b>{name}</b>!\n\n"
            "🔐 Админ-панель\nВыберите действие:",
            parse_mode="HTML",
            reply_markup=admin_menu()
        )
        return

    await add_user(
        message.from_user.id,
        message.from_user.username or "unknown",
        message.from_user.first_name or ""
    )
    await message.answer(
        f"👋 Привет, <b>{name}</b>!\n\n"
        "Здесь вы можете купить VPN-подписку на 30 дней.",
        parse_mode="HTML",
        reply_markup=main_menu()
    )


@router.callback_query(F.data == "buy_vpn")
async def buy_vpn(call: CallbackQuery, state: FSMContext):
    try:
        await call.message.edit_text("Введите имя для VPN (латиницей):")
        await set_last_message(call.from_user.id, call.message.message_id)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await state.set_state(BuyState.waiting_for_name)
    await call.answer()


@router.message(BuyState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip().replace(" ", "_")[:30]
    await state.clear()

    payment = create_payment(message.from_user.id)
    if payment:
        sent = await message.answer(
            f"💳 Счёт на {cfg.PAYMENT_PRICE} ₽\n\n"
            f"После оплаты конфиг придёт автоматически в течение 30 секунд.",
            reply_markup=payment_keyboard(payment["confirmation_url"])
        )
        await set_last_message(message.from_user.id, sent.message_id)
    else:
        await message.answer("❌ Ошибка платежа. Обратитесь в поддержку.")


@router.callback_query(F.data == "check_payment")
async def check_payment_cb(call: CallbackQuery):
    """Кнопка «Я оплатил» — только уведомляет. Клиента создаёт вебхук ЮKassa."""
    await call.answer(
        "✅ Оплата проверяется автоматически.\n"
        "Через 5–30 секунд вы получите конфиг в этот чат.",
        show_alert=True
    )


@router.callback_query(F.data == "my_sub")
async def my_sub(call: CallbackQuery):
    user = await get_user(call.from_user.id)
    if user and user["is_active"]:
        text = f"📋 Активна до: {user['paid_until']}"
    else:
        text = "Нет активной подписки."

    try:
        await call.message.edit_text(text, reply_markup=main_menu())
        await set_last_message(call.from_user.id, call.message.message_id)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await call.answer()


# ---------- Инструкции по платформам ----------

@router.callback_query(F.data == "help_android")
async def help_android(call: CallbackQuery):
    text = (
        "🤖 <b>Установка AmneziaWG на Android</b>\n\n"
        "1. Google Play → <b>AmneziaWG</b>\n"
        "2. Скачайте <code>vpn.conf</code>\n"
        "3. AmneziaWG → <b>➕</b> → «Импорт из файла»\n"
        "4. Выберите <code>vpn.conf</code>\n"
        "5. Переключатель → «Подключено»"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=install_help_keyboard())
    await call.answer()


@router.callback_query(F.data == "help_ios")
async def help_ios(call: CallbackQuery):
    text = (
        "🍎 <b>Установка AmneziaWG на iOS</b>\n\n"
        "1. App Store → <b>AmneziaWG</b>\n"
        "2. Скачайте <code>vpn.conf</code>\n"
        "3. AmneziaWG → <b>➕</b> → «Импорт из файла»\n"
        "4. Выберите <code>vpn.conf</code>\n"
        "5. Переключатель\n\n"
        "⚠️ Если App Store не открывается — используйте <b>DefaultVPN</b>."
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=install_help_keyboard())
    await call.answer()


@router.callback_query(F.data == "help_windows")
async def help_windows(call: CallbackQuery):
    text = (
        "🪟 <b>Установка AmneziaWG на Windows</b>\n\n"
        "1. amnezia.org/downloads → AmneziaWG Windows\n"
        "2. Сохраните <code>vpn.conf</code>\n"
        "3. AmneziaWG → Import Configuration\n"
        "4. Выберите <code>vpn.conf</code> → Connect"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=install_help_keyboard())
    await call.answer()


@router.callback_query(F.data == "help_macos")
async def help_macos(call: CallbackQuery):
    text = (
        "💻 <b>Установка AmneziaWG на macOS</b>\n\n"
        "1. App Store → AmneziaWG\n"
        "2. Скачайте <code>vpn.conf</code>\n"
        "3. AmneziaWG → Import tunnel(s) from file\n"
        "4. Найдите <code>vpn.conf</code> → Import → Allow → Activate"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=install_help_keyboard())
    await call.answer()