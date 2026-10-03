from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import add_user, get_user, update_subscription
from awg_client import awg
from payments import create_payment
from bot.keyboards import main_menu, payment_keyboard, install_help_keyboard
from config import cfg

router = Router()


class BuyState(StatesGroup):
    waiting_for_name = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await add_user(message.from_user.id, message.from_user.username or "unknown")
    await message.answer("👋 Добро пожаловать!", reply_markup=main_menu())


@router.callback_query(F.data == "buy_vpn")
async def buy_vpn(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введите имя для VPN (латиницей):")
    await state.set_state(BuyState.waiting_for_name)
    await call.answer()


@router.message(BuyState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip().replace(" ", "_")[:30]
    await state.clear()
    payment = create_payment(message.from_user.id)
    if payment:
        await message.answer(
            f"💳 Счёт на {cfg.PAYMENT_PRICE} ₽",
            reply_markup=payment_keyboard(payment["confirmation_url"])
        )
    else:
        await message.answer("❌ Ошибка платежа")


@router.callback_query(F.data == "check_payment")
async def check_payment_cb(call: CallbackQuery):
    user = await get_user(call.from_user.id)
    if not user:
        await call.answer("Сначала создайте платёж", show_alert=True)
        return

    client_name = f"user_{call.from_user.id}"
    client = await awg.create_client(client_name)
    if not client:
        await call.message.answer("❌ Ошибка создания клиента")
        return

    config_text = await awg.get_client_config(client["id"])
    if not config_text:
        await call.message.answer("❌ Ошибка получения конфига")
        return

    await update_subscription(call.from_user.id, client_name, client["id"], cfg.SUBSCRIPTION_DAYS)
    await call.message.answer_document(
        document=("vpn.conf", config_text.encode()),
        caption=f"✅ Оплата получена! Ваш VPN-конфиг на {cfg.SUBSCRIPTION_DAYS} дней."
    )
    await call.message.answer(
        "📱 Выберите ваше устройство, чтобы получить инструкцию по установке:",
        reply_markup=install_help_keyboard()
    )


@router.callback_query(F.data == "my_sub")
async def my_sub(call: CallbackQuery):
    user = await get_user(call.from_user.id)
    if user and user["is_active"]:
        await call.message.answer(f"📋 Активна до: {user['paid_until']}")
    else:
        await call.message.answer("Нет активной подписки.")
    await call.answer()


# ---------- Инструкции ----------

@router.callback_query(F.data == "help_android")
async def help_android(call: CallbackQuery):
    text = (
        "🤖 <b>Установка AmneziaWG на Android</b>\n\n"
        "1. Откройте Google Play и установите <b>AmneziaWG</b> (Android 7.0+).\n\n"
        "2. Скачайте <code>vpn.conf</code> из этого чата (папка «Загрузки»).\n\n"
        "3. Откройте AmneziaWG → иконка <b>➕</b> справа снизу.\n\n"
        "4. Выберите <b>«Импорт из файла или архива»</b>.\n\n"
        "5. Найдите <code>vpn.conf</code> и выберите его.\n\n"
        "6. Нажмите переключатель справа от названия подключения.\n\n"
        "7. Статус <b>«Подключено»</b> — готово!"
    )
    await call.message.answer(text, parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data == "help_ios")
async def help_ios(call: CallbackQuery):
    text = (
        "🍎 <b>Установка AmneziaWG на iOS</b>\n\n"
        "1. Откройте App Store и установите <b>AmneziaWG</b> (iOS 15.0+).\n\n"
        "2. Скачайте <code>vpn.conf</code> из этого чата.\n\n"
        "3. Откройте AmneziaWG → иконка <b>➕</b>.\n\n"
        "4. Выберите <b>«Импорт из файла»</b> и найдите <code>vpn.conf</code>.\n\n"
        "5. После импорта нажмите переключатель для подключения.\n\n"
        "⚠️ <b>Если App Store не открывается:</b>\n"
        "В российском App Store приложение недоступно. "
        "Используйте <b>DefaultVPN</b> (доступен в РФ) или смените регион."
    )
    await call.message.answer(text, parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data == "help_windows")
async def help_windows(call: CallbackQuery):
    text = (
        "🪟 <b>Установка AmneziaWG на Windows</b>\n\n"
        "1. Скачайте <b>AmneziaWG для Windows</b> с amnezia.org/downloads.\n\n"
        "2. Сохраните <code>vpn.conf</code> в удобную папку (например, <code>C:\\VPN</code>).\n\n"
        "3. Запустите AmneziaWG.\n\n"
        "4. Нажмите <b>«Import Configuration»</b> и выберите файл.\n\n"
        "5. Нажмите <b>«Connect»</b>. Готово!"
    )
    await call.message.answer(text, parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data == "help_macos")
async def help_macos(call: CallbackQuery):
    text = (
        "💻 <b>Установка AmneziaWG на macOS</b>\n\n"
        "1. Откройте App Store и установите <b>AmneziaWG</b> (macOS 12.0+).\n\n"
        "2. Скачайте <code>vpn.conf</code> из этого чата.\n\n"
        "3. Откройте AmneziaWG → <b>«Import tunnel(s) from file»</b>.\n\n"
        "4. Найдите <code>vpn.conf</code> → <b>Import</b>.\n\n"
        "5. Разрешите добавление VPN-конфигурации (<b>Allow</b>).\n\n"
        "6. Выберите туннель → <b>Activate</b>."
    )
    await call.message.answer(text, parse_mode="HTML")
    await call.answer()