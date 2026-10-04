"""Обработчики админ-панели: статистика, управление клиентами, все конфиги."""
import aiosqlite
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest

from database import (
    get_admin_stats, get_all_clients, get_user,
    extend_subscription, deactivate_user,
    set_last_message, get_last_message
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


async def safe_edit(call: CallbackQuery, text: str,
                    reply_markup=None, parse_mode="HTML"):
    """Удаляет предыдущее сообщение бота и редактирует/отправляет новое."""