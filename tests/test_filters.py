import pytest
from unittest.mock import MagicMock
from bot.filters import IsAdmin

@pytest.mark.asyncio
async def test_is_admin_true(monkeypatch):
    from config import cfg
    monkeypatch.setattr(cfg, "ADMIN_ID", 123)
    event = MagicMock()
    event.from_user.id = 123
    f = IsAdmin()
    assert await f(event) is True

@pytest.mark.asyncio
async def test_is_admin_false(monkeypatch):
    from config import cfg
    monkeypatch.setattr(cfg, "ADMIN_ID", 123)
    event = MagicMock()
    event.from_user.id = 999
    f = IsAdmin()
    assert await f(event) is False