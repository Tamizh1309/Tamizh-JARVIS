import aiosqlite
from typing import List, Dict, Any, Optional
from datetime import datetime
from config.settings import get_settings


class LongTermMemory:
    """Async SQLite persistent memory store for tasks, study logs, and facts."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = db_path
        else:
            settings = get_settings()
            raw = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
            self.db_path = raw or "./jarvis.db"
        self._conn: Optional[aiosqlite.Connection] = None

    async def get_connection(self) -> aiosqlite.Connection:
        if self._conn is None:
            self._conn = await aiosqlite.connect(self.db_path)
            self._conn.row_factory = aiosqlite.Row
        return self._conn

    async def close(self):
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def init_db(self):
        db = await self.get_connection()
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'MEDIUM',
                status TEXT DEFAULT 'PENDING',
                created_at TEXT,
                due_date TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                created_at TEXT,
                notes TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                updated_at TEXT
            )
        """)
        await db.commit()

        # Seed default tasks if empty
        cursor = await db.execute("SELECT COUNT(*) FROM tasks")
        count = (await cursor.fetchone())[0]
        if count == 0:
            now = datetime.now().isoformat()
            await db.execute(
                "INSERT INTO tasks (title, description, priority, status, created_at) VALUES (?, ?, ?, ?, ?)",
                ("Revise DBMS Transactions", "Review ACID properties and 2PL locking protocols.", "HIGH", "PENDING", now)
            )
            await db.execute(
                "INSERT INTO tasks (title, description, priority, status, created_at) VALUES (?, ?, ?, ?, ?)",
                ("Solve 2 DSA Dynamic Programming problems", "Focus on 0/1 Knapsack and LCS variants.", "MEDIUM", "PENDING", now)
            )
            await db.execute(
                "INSERT INTO tasks (title, description, priority, status, created_at) VALUES (?, ?, ?, ?, ?)",
                ("Complete Computer Networks Quiz 4", "TCP sliding window and congestion control.", "LOW", "PENDING", now)
            )
            await db.commit()

    # --- Task Operations ---
    async def create_task(self, title: str, description: str = "", priority: str = "MEDIUM", due_date: str = None) -> int:
        await self.init_db()
        now = datetime.now().isoformat()
        db = await self.get_connection()
        cursor = await db.execute(
            "INSERT INTO tasks (title, description, priority, status, created_at, due_date) VALUES (?, ?, ?, 'PENDING', ?, ?)",
            (title, description, priority.upper(), now, due_date)
        )
        await db.commit()
        return cursor.lastrowid

    async def list_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        await self.init_db()
        db = await self.get_connection()
        if status:
            cursor = await db.execute("SELECT * FROM tasks WHERE status = ? ORDER BY id DESC", (status.upper(),))
        else:
            cursor = await db.execute("SELECT * FROM tasks ORDER BY id DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def update_task_status(self, task_id: int, status: str) -> bool:
        await self.init_db()
        db = await self.get_connection()
        cursor = await db.execute("UPDATE tasks SET status = ? WHERE id = ?", (status.upper(), task_id))
        await db.commit()
        return cursor.rowcount > 0

    # --- Study Operations ---
    async def log_study_session(self, subject: str, topic: str, duration_minutes: int, notes: str = "") -> int:
        await self.init_db()
        now = datetime.now().isoformat()
        db = await self.get_connection()
        cursor = await db.execute(
            "INSERT INTO study_sessions (subject, topic, duration_minutes, created_at, notes) VALUES (?, ?, ?, ?, ?)",
            (subject, topic, duration_minutes, now, notes)
        )
        await db.commit()
        return cursor.lastrowid

    async def get_study_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        await self.init_db()
        db = await self.get_connection()
        cursor = await db.execute("SELECT * FROM study_sessions ORDER BY id DESC LIMIT ?", (limit,))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def get_today_study_minutes(self) -> int:
        await self.init_db()
        today_prefix = datetime.now().strftime("%Y-%m-%d")
        db = await self.get_connection()
        cursor = await db.execute(
            "SELECT COALESCE(SUM(duration_minutes), 0) FROM study_sessions WHERE created_at LIKE ?",
            (f"{today_prefix}%",)
        )
        row = await cursor.fetchone()
        return int(row[0]) if row else 0

    # --- Fact / Knowledge Operations ---
    async def set_fact(self, category: str, key: str, value: str):
        await self.init_db()
        now = datetime.now().isoformat()
        db = await self.get_connection()
        await db.execute("""
            INSERT INTO facts (category, key, value, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
        """, (category, key, value, now))
        await db.commit()

    async def get_facts(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        await self.init_db()
        db = await self.get_connection()
        if category:
            cursor = await db.execute("SELECT * FROM facts WHERE category = ?", (category,))
        else:
            cursor = await db.execute("SELECT * FROM facts")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
