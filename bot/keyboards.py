"""Inline-клавиатуры для пользователя и администратора."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> InlineKeyboardMarkup:
    """Главное меню пользователя."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Купить VPN", callback_data="buy_vpn")],
        [InlineKeyboardButton(text="📋 Моя подписка", callback_data="my_sub")],
    ])


def payment_keyboard(url: str) -> InlineKeyboardMarkup:
    """Клавиатура после создания счёта: ссылка на оплату + проверка."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить", url=url)],
        [InlineKeyboardButton(text="Я оплатил", callback_data="check_payment")],
    ])


def install_help_keyboard() -> InlineKeyboardMarkup:
    """4 кнопки с инструкциями по платформам."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Android", callback_data="help_android")],
        [InlineKeyboardButton(text="🍎 iOS", callback_data="help_ios")],
        [InlineKeyboardButton(text="🪟 Windows", callback_data="help_windows")],
        [InlineKeyboardButton(text="💻 macOS", callback_data="help_macos")],
    ])


def admin_menu() -> InlineKeyboardMarkup:
    """Главное меню администратора."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Общая статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Управление клиентами", callback_data="admin_clients")],
        [InlineKeyboardButton(text="📋 Все конфиги", callback_data="admin_configs")],
    ])


def admin_stats_keyboard() -> InlineKeyboardMarkup:
    """Кнопки под статистикой: обновить и назад."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")],
    ])


def clients_list_keyboard(clients: list) -> InlineKeyboardMarkup:
    """Список клиентов с эмодзи статуса (🟢/🔴)."""
    buttons = []
    for c in clients:
        status = "🟢" if c["is_active"] else "🔴"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {c['client_name'] or c['user_id']}",
                callback_data=f"admin_client_{c['user_id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def client_manage_keyboard(user_id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Кнопки управления конкретным клиентом."""
    status_btn = "🔓 Разблокировать" if not is_active else "🔒 Заблокировать"
    status_action = "enable" if not is_active else "disable"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏳ Продлить +30 дней", callback_data=f"admin_extend_{user_id}_30")],
        [InlineKeyboardButton(text="⏳ Продлить +7 дней", callback_data=f"admin_extend_{user_id}_7")],
        [InlineKeyboardButton(text="✏️ Продлить на N дней", callback_data=f"admin_extend_custom_{user_id}")],
        [InlineKeyboardButton(text=status_btn, callback_data=f"admin_{status_action}_{user_id}")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"admin_delete_{user_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_clients")],
    ])