"""Тесты админ-панели."""
import pytest


@pytest.mark.asyncio
async def test_admin_panel_opens(fake_message):
    from bot.admin_handlers import admin_panel
    await admin_panel(fake_message)
    fake_message.answer.assert_awaited_once()


@pytest.mark.asyncio
async def test_show_stats(temp_db, fake_callback, monkeypatch):
    await temp_db.add_user(1, "u1")
    await temp_db.update_subscription(1, "c1", "cid1", 30)
    await temp_db.record_payment(1, 300.0, "p1")
    monkeypatch.setattr("bot.admin_handlers.get_admin_stats", temp_db.get_admin_stats)
    from bot.admin_handlers import show_stats
    await show_stats(fake_callback)
    text = fake_callback.message.edit_text.call_args[0][0]
    assert "300" in text


@pytest.mark.asyncio
async def test_show_clients_empty(temp_db, fake_callback, monkeypatch):
    monkeypatch.setattr("bot.admin_handlers.get_all_clients", temp_db.get_all_clients)
    from bot.admin_handlers import show_clients
    await show_clients(fake_callback)
    text = fake_callback.message.edit_text.call_args[0][0]
    assert "Нет клиентов" in text