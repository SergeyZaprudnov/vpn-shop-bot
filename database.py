"""Модуль для работы с базой данных SQLite через aiosqlite."""
import os
import aiosqlite
from datetime import datetime, timedelta

DB_PATH = os.getenv("DB_PATH", "vpn_bot.db")


async def init_db():
    """Создаёт таблицы users и payments при первом запуске."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                client_name TEXT UNIQUE,
                client_id TEXT,
                paid_until TEXT,
                is_active INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                payment_id TEXT UNIQUE,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def add_user(user_id: int, username: str):
    """Добавляет пользователя или игнорирует дубликат."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        await db.commit()


async def get_user(user_id: int):
    """Возвращает запись пользователя или None."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            return await cur.fetchone()


async def update_subscription(user_id: int, client_name: str, client_id: str, days: int):
    """Активирует подписку: привязывает client_id и устанавливает paid_until."""
    paid_until = (datetime.now() + timedelta(days=days)).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users SET client_name=?, client_id=?, paid_until=?, is_active=1
            WHERE user_id=?
        """, (client_name, client_id, paid_until, user_id))
        await db.commit()


async def get_expiring_users(days_before: int):
    """Пользователи, у которых подписка истекает ровно через N дней."""
    target = (datetime.now() + timedelta(days=days_before)).date().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE is_active=1 AND date(paid_until)=?",
            (target,)
        ) as cur:
            return await cur.fetchall()


async def get_expired_users():
    """Пользователи с истёкшей подпиской, но ещё активные."""
    today = datetime.now().date().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE is_active=1 AND date(paid_until)<?",
            (today,)
        ) as cur:
            return await cur.fetchall()


async def deactivate_user(user_id: int):
    """Ставит is_active=0 (блокировка без удаления)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET is_active=0 WHERE user_id=?", (user_id,))
        await db.commit()


async def extend_subscription(user_id: int, days: int):
    """Продлевает подписку на N дней от текущей даты paid_until."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT paid_until FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            if row and row["paid_until"]:
                current = datetime.fromisoformat(row["paid_until"])
                new_date = current + timedelta(days=days)
                await db.execute(
                    "UPDATE users SET paid_until=?, is_active=1 WHERE user_id=?",
                    (new_date.isoformat(), user_id)
                )
            await db.commit()


async def record_payment(user_id: int, amount: float, payment_id: str):
    """Записывает успешный платёж в таблицу payments."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO payments (user_id, amount, payment_id, status) "
            "VALUES (?, ?, ?, 'succeeded')",
            (user_id, amount, payment_id)
        )
        await db.commit()


async def get_admin_stats() -> dict:
    """Возвращает статистику для админ-панели."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT COUNT(*) as cnt FROM users WHERE client_id IS NOT NULL") as cur:
            total = (await cur.fetchone())["cnt"]
        async with db.execute("SELECT COUNT(*) as cnt FROM users WHERE is_active=1 AND client_id IS NOT NULL") as cur:
            online = (await cur.fetchone())["cnt"]
        async with db.execute("SELECT COUNT(*) as cnt FROM users WHERE is_active=0 AND client_id IS NOT NULL") as cur:
            blocked = (await cur.fetchone())["cnt"]
        async with db.execute("SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE status='succeeded'") as cur:
            revenue = (await cur.fetchone())["total"]
        return {
            "total_clients": total,
            "online_clients": online,
            "blocked_clients": blocked,
            "total_revenue": revenue,
        }


async def get_all_clients() -> list:
    """Возвращает всех клиентов для админ-списка."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT user_id, username, client_name, client_id, paid_until, is_active
            FROM users WHERE client_id IS NOT NULL
            ORDER BY created_at DESC
        """) as cur:
            return await cur.fetchall()