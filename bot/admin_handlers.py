"""Обработчики админ-панели: статистика, управление клиентами."""
import aiosqlite
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest

from database import (
    get_admin_stats, get_all_clients, get_user,
    extend_subscription, deactivate_user
)
from awg_client import awg
from bot.keyboards import (
    admin_menu, admin_stats_keyboard,
    clients_list_keyboard, client_manage_keyboard
)
from bot.filters import IsAdmin

router = Router()


class AdminState(StatesGroup):
    """Состояние ожидания количества дней при продлении."""
    waiting_for_days = State()


@router.message(Command("admin"), IsAdmin())
async def admin_panel(message: Message):
    """Открывает админ-панель по команде /admin."""
    await message.answer("🔐 Админ-панель", reply_markup=admin_menu())


@router.callback_query(F.data == "admin_menu", IsAdmin())
async def back_admin(call: CallbackQuery):
    """Возврат в главное меню админки. Заменяет текущее сообщение."""
    try:
        await call.message.edit_text("🔐 Админ-панель", reply_markup=admin_menu())
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await call.answer()


@router.callback_query(F.data == "admin_stats", IsAdmin())
async def show_stats(call: CallbackQuery):
    """Показывает статистику: всего, онлайн, заблокировано, сумма оплат."""
    s = await get_admin_stats()
    text = (
        "📊 <b>Статистика</b>\n\n"
        f"👥 Всего: <b>{s['total_clients']}</b>\n"
        f"🟢 Онлайн: <b>{s['online_clients']}</b>\n"
        f"🔴 Заблок: <b>{s['blocked_clients']}</b>\n"
        f"💰 Сумма: <b>{s['total_revenue']:.2f} ₽</b>"
    )
    try:
        await call.message.edit_text(
            text, parse_mode="HTML",
            reply_markup=admin_stats_keyboard()
        )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await call.answer("Данные не изменились")
            return
        raise
    await call.answer("Статистика обновлена")


@router.callback_query(F.data == "admin_clients", IsAdmin())
async def show_clients(call: CallbackQuery):
    """Показывает список всех клиентов. Заменяет текущее сообщение."""
    clients = await get_all_clients()
    if not clients:
        text = "Нет клиентов."
        kb = admin_menu()
    else:
        text = "👥 Выберите:"
        kb = clients_list_keyboard(clients)

    try:
        await call.message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await call.answer()


@router.callback_query(F.data.startswith("admin_client_"), IsAdmin())
async def manage_client(call: CallbackQuery):
    """Карточка клиента с кнопками действий. Заменяет текущее сообщение."""
    uid = int(call.data.split("_")[-1])
    u = await get_user(uid)
    if not u or not u["client_id"]:
        await call.answer("Не найден", show_alert=True)
        return

    status = "🟢 Активен" if u["is_active"] else "🔴 Заблокирован"
    text = (
        f"👤 <b>{u['client_name']}</b>\n\n"
        f"Статус: {status}\n"
        f"До: <code>{u['paid_until']}</code>\n"
        f"ID: <code>{uid}</code>"
    )
    try:
        await call.message.edit_text(
            text, parse_mode="HTML",
            reply_markup=client_manage_keyboard(uid, bool(u["is_active"]))
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await call.answer()


@router.callback_query(F.data.startswith("admin_disable_"), IsAdmin())
async def disable_cb(call: CallbackQuery):
    """Блокирует клиента."""
    uid = int(call.data.split("_")[-1])
    u = await get_user(uid)
    if u and u["client_id"] and await awg.disable_client(u["client_id"]):
        await deactivate_user(uid)
        await call.answer("🔒 Заблокирован")
        await manage_client(call)
    else:
        await call.answer("❌ Ошибка блокировки", show_alert=True)


@router.callback_query(F.data.startswith("admin_enable_"), IsAdmin())
async def enable_cb(call: CallbackQuery):
    """Разблокирует клиента."""
    uid = int(call.data.split("_")[-1])
    u = await get_user(uid)
    if u and u["client_id"] and await awg.enable_client(u["client_id"]):
        await extend_subscription(uid, 0)
        await call.answer("🔓 Разблокирован")
        await manage_client(call)
    else:
        await call.answer("❌ Ошибка разблокировки", show_alert=True)


@router.callback_query(F.data.startswith("admin_extend_"), IsAdmin())
async def extend_fixed(call: CallbackQuery):
    """Продление на фиксированное число дней (7 или 30)."""
    parts = call.data.split("_")
    uid, days = int(parts[2]), int(parts[3])
    await extend_subscription(uid, days)
    u = await get_user(uid)
    if u and u["client_id"]:
        await awg.enable_client(u["client_id"])
    await call.answer(f"⏳ +{days} дней")
    await manage_client(call)


@router.callback_query(F.data.startswith("admin_extend_custom_"), IsAdmin())
async def extend_custom_start(call: CallbackQuery, state: FSMContext):
    """Запрашивает произвольное число дней."""
    uid = int(call.data.split("_")[-1])
    await state.update_data(uid=uid)
    await state.set_state(AdminState.waiting_for_days)
    try:
        await call.message.edit_text(
            "Введите количество дней:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="◀️ Отмена", callback_data=f"admin_client_{uid}")
            ]])
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await call.answer()


@router.message(AdminState.waiting_for_days, IsAdmin())
async def extend_custom_finish(message: Message, state: FSMContext):
    """Обрабатывает ввод количества дней. Отправляет новое сообщение."""
    try:
        days = int(message.text.strip())
        if days <= 0 or days > 3650:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите число от 1 до 3650:")
        return

    data = await state.get_data()
    uid = data["uid"]
    await state.clear()
    await extend_subscription(uid, days)

    u = await get_user(uid)
    if u and u["client_id"]:
        await awg.enable_client(u["client_id"])
    await message.answer(f"✅ Продлён на {days} дней")


@router.callback_query(F.data.startswith("admin_delete_"), IsAdmin())
async def delete_cb(call: CallbackQuery):
    """Удаляет клиента из панели и БД."""
    uid = int(call.data.split("_")[-1])
    u = await get_user(uid)
    if u and u["client_id"]:
        await awg.delete_client(u["client_id"])
        async with aiosqlite.connect("vpn_bot.db") as db:
            await db.execute("DELETE FROM users WHERE user_id=?", (uid,))
            await db.commit()
        await call.answer("🗑 Удалён")
        await show_clients(call)
    else:
        await call.answer("Клиент не найден", show_alert=True)