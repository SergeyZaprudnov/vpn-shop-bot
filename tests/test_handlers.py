import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_cmd_start_adds_user(temp_db, fake_message, monkeypatch):
    monkeypatch.setattr("bot.handlers.add_user", temp_db.add_user)
    from bot.handlers import cmd_start
    await cmd_start(fake_message)
    user = await temp_db.get_user(123456)
    assert user is not None

@pytest.mark.asyncio
async def test_check_payment_creates_client(temp_db, fake_callback, monkeypatch, mock_awg):
    await temp_db.add_user(123456, "testuser")
    monkeypatch.setattr("bot.handlers.awg", mock_awg)
    monkeypatch.setattr("bot.handlers.update_subscription", temp_db.update_subscription)
    monkeypatch.setattr("bot.handlers.get_user", temp_db.get_user)
    from bot.handlers import check_payment_cb
    await check_payment_cb(fake_callback)
    mock_awg.create_client.assert_awaited_once()

@pytest.mark.asyncio
async def test_help_android_sends_text(fake_callback):
    from bot.handlers import help_android
    await help_android(fake_callback)
    fake_callback.message.answer.assert_awaited_once()

@pytest.mark.asyncio
async def test_help_ios_mentions_alternative(fake_callback):
    from bot.handlers import help_ios
    await help_ios(fake_callback)
    text = fake_callback.message.answer.call_args[0][0]
    assert "DefaultVPN" in text or "App Store" in text