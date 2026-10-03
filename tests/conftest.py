"""Общие фикстуры для всех тестов."""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock


@pytest_asyncio.fixture
async def temp_db(tmp_path, monkeypatch):
    """Временная БД для каждого теста."""
    import database
    db_file = tmp_path / "test.db"
    monkeypatch.setattr(database, "DB_PATH", str(db_file))
    await database.init_db()
    yield database
    if db_file.exists():
        db_file.unlink()


@pytest.fixture
def mock_awg(monkeypatch):
    """Мок AWGClient, чтобы не ходить в реальный API."""
    mock = MagicMock()
    mock.create_client = AsyncMock(return_value={"id": "test_id", "name": "test"})
    mock.get_client_config = AsyncMock(return_value="[Interface]\nPrivateKey = test")
    mock.disable_client = AsyncMock(return_value=True)
    mock.enable_client = AsyncMock(return_value=True)
    mock.delete_client = AsyncMock(return_value=True)
    monkeypatch.setattr("awg_client.awg", mock)
    return mock


@pytest.fixture
def fake_message():
    """Фейковый Message от aiogram."""
    msg = MagicMock()
    msg.from_user.id = 123456
    msg.from_user.username = "test_user"
    msg.text = "/start"
    msg.answer = AsyncMock()
    msg.answer_document = AsyncMock()
    return msg


@pytest.fixture
def fake_callback():
    """Фейковый CallbackQuery от aiogram."""
    cb = MagicMock()
    cb.from_user.id = 123456
    cb.data = "buy_vpn"
    cb.message = MagicMock()
    cb.message.answer = AsyncMock()
    cb.message.edit_text = AsyncMock()
    cb.message.answer_document = AsyncMock()
    cb.answer = AsyncMock()
    return cb