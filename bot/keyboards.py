from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Купить VPN", callback_data="buy_vpn")],
        [InlineKeyboardButton(text="📋 Моя подписка", callback_data="my_sub")],
    ])

def payment_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить", url=url)],
        [InlineKeyboardButton(text="Я оплатил", callback_data="check_payment")],
    ])

def install_help_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Android", callback_data="help_android")],
        [InlineKeyboardButton(text="🍎 IOS", callback_data="help_ios")],
        [InlineKeyboardButton(text="🪟 Windows", callback_data="help_windows")],
        [InlineKeyboardButton(text="💻 macOS", callback_data="help_macos")],
    ])

def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Общая статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(tetx="👥 Управление клиентами", callback_data="admin_clients")],
    ])

def admin_stats_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")],
    ])

def clients_list_keyboard(clients: list):
    buttons = []
    for c in clients:
        status ="🟢" if c["is_active"] else "🔴"
        buttons.append([InlineKeyboardButton(text=f"{status} {c['client_name'] or c['user_id']}",
                        callback_data=f"admin_client_{c['user_id']}")])
        buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

def client_manage_keyboard(user_id: int, is_active: bool):
    status_btn = "🔓 Разблокировать" if not is_active else "🔒 Заблокировать"
    status_action = "enable" if not is_active else "disable"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏳ Продлить +30 дней", callback_data=f"admin_extend_{user_id}_30")],
        [InlineKeyboardButton(text="⏳ Продлить +7 дней", callback_data=f"admin_extend_{user_id}_7")],
        [InlineKeyboardButton(text="✏️ Продлить на N дней", callback_data=f"admin_extend_custom_{user_id}")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"admin_delete_{user_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"admin_clients")],
    ])
