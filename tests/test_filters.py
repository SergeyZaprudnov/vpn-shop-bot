"""Тесты фильтра IsAdmin."""
import pytest
from unittest.mock import MagicMock
from bot.filters import IsAdmin


@pytest.mark.asyncio
async def test_is_admin_true(monkeypatch):
    import config
    monkeypatch.setattr(config.cfg, "ADMIN_ID", 123)
    event = MagicMock()
    event.from_user.id = 123
    assert await IsAdmin()(event) is True


@pytest.mark.asyncio
async def test_is_admin_false(monkeypatch):
    import config
    monkeypatch.setattr(config.cfg, "ADMIN_ID", 123)
    event = MagicMock()
    event.from_user.id = 999
    assert await IsAdmin()(event) is False