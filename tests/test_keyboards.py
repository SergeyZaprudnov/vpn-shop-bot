"""Тесты структуры клавиатур."""
from bot.keyboards import install_help_keyboard, clients_list_keyboard, client_manage_keyboard


def test_install_help_keyboard_has_4_platforms():
    kb = install_help_keyboard()
    callbacks = {b[0].callback_data for b in kb.inline_keyboard}
    assert callbacks == {"help_android", "help_ios", "help_windows", "help_macos"}


def test_clients_list_keyboard_with_status():
    clients = [
        {"user_id": 1, "client_name": "active", "is_active": 1},
        {"user_id": 2, "client_name": "blocked", "is_active": 0},
    ]
    kb = clients_list_keyboard(clients)
    texts = [b[0].text for b in kb.inline_keyboard]
    assert any("🟢" in t for t in texts)
    assert any("🔴" in t for t in texts)


def test_client_manage_keyboard_active():
    kb = client_manage_keyboard(123, is_active=True)
    callbacks = [b[0].callback_data for b in kb.inline_keyboard]
    assert any("admin_disable_123" in c for c in callbacks)
    assert any("admin_extend_123_30" in c for c in callbacks)