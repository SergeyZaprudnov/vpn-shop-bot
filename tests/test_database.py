import aiosqlite
import pytest
from datetime import datetime

@pytest.mark.asyncio
async def test_init_db_created_tables(temp_db):
    import aiosqlite
    async with aiosqlite.connect(temp_db.DB_PATH) as db:
        async with db.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
            tables = {row[0] for row in await cursor.fetchall()}
    assert "users" in tables
    assert "payments" in tables

@pytest.mark.asyncio
async def test_add_and_get_user(temp_db):
    await temp_db.add_user(123, "testuser")
    user = await temp_db.get_user(123)
    assert user is not None
    assert user["user_id"] == 123

@pytest.mark.asyncio
async def test_update_subscription(temp_db):
    await temp_db.add_user(123, "testuser")
    user = await temp_db.get_user(123)
    assert user["client_name"] == "client_1"
    assert user["is_active"] == 1

@pytest.mark.asyncio
async def test_extend_subscription(temp_db):
    await temp_db.add_user(123, "testuser")
    await temp_db.update_subscription(123, "client_1", "cid_1", 10)
    user_before = await temp_db.get_user(123)
    date_before = datetime.fromisoformat(user_before["paid_until"])
    await temp_db.extend_subscription(123, 30)
    user_after = await temp_db.get_user(123)
    date_after = datetime.fromisoformat(user_after["paid_until"])
    assert (date_after - date_before).days == 30

@pytest.mark.asyncio
async def test_get_admin_status(temp_db):
    await temp_db.add_user(1, "user1")
    await temp_db.add_user(2, "user2")
    await temp_db.update_subscription(1, "c1", "cid1", 30)
    await temp_db.update_subscription(2, "c2", "cid2", 30)
    await temp_db.deactivate_user(2)
    await temp_db.record_payment(1, 300.0, "p1")
    status = await temp_db.get_admin_status()
    assert status["total_clients"] == 2
    assert status["online_clients"] == 1
    assert status["blocked_clients"] == 1
    assert status["total_revenue"] == 300.0
