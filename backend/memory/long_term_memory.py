import aiosqlite
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from config.settings import get_settings


class LongTermMemory:
    """Async SQLite persistent store for tasks, study logs, memory records, and facts."""

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

        # 1. Tasks Table with complete schema
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                status TEXT DEFAULT 'PENDING',
                priority TEXT DEFAULT 'MEDIUM',
                created_at TEXT,
                due_at TEXT,
                completed_at TEXT,
                category TEXT DEFAULT 'GENERAL',
                source TEXT DEFAULT 'USER'
            )
        """)

        # Migration: Check if older columns exist or need addition
        cursor = await db.execute("PRAGMA table_info(tasks)")
        existing_cols = [row["name"] for row in await cursor.fetchall()]
        if "due_at" not in existing_cols:
            await db.execute("ALTER TABLE tasks ADD COLUMN due_at TEXT")
        if "completed_at" not in existing_cols:
            await db.execute("ALTER TABLE tasks ADD COLUMN completed_at TEXT")
        if "category" not in existing_cols:
            await db.execute("ALTER TABLE tasks ADD COLUMN category TEXT DEFAULT 'GENERAL'")
        if "source" not in existing_cols:
            await db.execute("ALTER TABLE tasks ADD COLUMN source TEXT DEFAULT 'USER'")

        # 2. Study Sessions Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                created_at TEXT,
                notes TEXT DEFAULT '',
                session_type TEXT DEFAULT 'STUDY',
                score REAL DEFAULT 0.0
            )
        """)

        # 3. Facts Table (legacy/general)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                updated_at TEXT
            )
        """)

        # 4. Structured Memory Records Table (Phase 4 Section 6)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS memory_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                metadata TEXT DEFAULT '{}',
                created_at TEXT,
                updated_at TEXT,
                UNIQUE(category, key)
            )
        """)
        await db.commit()

        # Seed initial tasks if table is empty
        cursor = await db.execute("SELECT COUNT(*) FROM tasks")
        count = (await cursor.fetchone())[0]
        if count == 0:
            now = datetime.now().isoformat()
            await db.execute(
                "INSERT INTO tasks (title, description, priority, status, created_at, category, source) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("Revise DBMS Transactions", "Review ACID properties and 2PL locking protocols.", "HIGH", "PENDING", now, "STUDY", "SYSTEM")
            )
            await db.execute(
                "INSERT INTO tasks (title, description, priority, status, created_at, category, source) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("Solve 2 DSA Dynamic Programming problems", "Focus on 0/1 Knapsack and LCS variants.", "MEDIUM", "PENDING", now, "DSA", "SYSTEM")
            )
            await db.execute(
                "INSERT INTO tasks (title, description, priority, status, created_at, category, source) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("Complete Computer Networks Quiz 4", "TCP sliding window and congestion control.", "LOW", "PENDING", now, "QUIZ", "SYSTEM")
            )
            await db.commit()

    # --- Task Operations (Section 5) ---

    async def create_task(
        self,
        title: str,
        description: str = "",
        priority: str = "MEDIUM",
        due_at: Optional[str] = None,
        category: str = "GENERAL",
        source: str = "USER"
    ) -> int:
        await self.init_db()
        now = datetime.now().isoformat()
        db = await self.get_connection()
        cursor = await db.execute(
            """INSERT INTO tasks 
               (title, description, priority, status, created_at, due_at, category, source) 
               VALUES (?, ?, ?, 'PENDING', ?, ?, ?, ?)""",
            (title.strip(), description.strip(), priority.upper(), now, due_at, category.upper(), source)
        )
        await db.commit()
        return cursor.lastrowid

    async def list_tasks(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        await self.init_db()
        db = await self.get_connection()
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status.upper())
        if category:
            query += " AND category = ?"
            params.append(category.upper())
        query += " ORDER BY id DESC"
        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        await self.init_db()
        db = await self.get_connection()
        cursor = await db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def update_task(self, task_id: int, updates: Dict[str, Any]) -> bool:
        await self.init_db()
        db = await self.get_connection()
        allowed_fields = ["title", "description", "status", "priority", "due_at", "category"]
        set_clauses = []
        params = []
        for k, v in updates.items():
            if k in allowed_fields:
                set_clauses.append(f"{k} = ?")
                params.append(v.upper() if k in ["status", "priority", "category"] and isinstance(v, str) else v)

        if not set_clauses:
            return False

        if "status" in updates and updates["status"].upper() == "COMPLETED":
            set_clauses.append("completed_at = ?")
            params.append(datetime.now().isoformat())

        params.append(task_id)
        query = f"UPDATE tasks SET {', '.join(set_clauses)} WHERE id = ?"
        cursor = await db.execute(query, params)
        await db.commit()
        return cursor.rowcount > 0

    async def complete_task(self, task_id: int) -> bool:
        return await self.update_task(task_id, {"status": "COMPLETED"})

    async def update_task_status(self, task_id: int, status: str) -> bool:
        return await self.update_task(task_id, {"status": status})

    async def delete_task(self, task_id: int, soft_delete: bool = False) -> bool:
        await self.init_db()
        db = await self.get_connection()
        if soft_delete:
            cursor = await db.execute("UPDATE tasks SET status = 'DELETED' WHERE id = ?", (task_id,))
        else:
            cursor = await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        await db.commit()
        return cursor.rowcount > 0

    # --- Structured Memory Operations (Section 6) ---

    async def create_memory(
        self,
        category: str,
        key: str,
        value: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        await self.init_db()
        now = datetime.now().isoformat()
        val_str = json.dumps(value) if not isinstance(value, str) else value
        meta_str = json.dumps(metadata or {})
        db = await self.get_connection()
        await db.execute("""
            INSERT INTO memory_records (category, key, value, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(category, key) DO UPDATE SET
                value=excluded.value,
                metadata=excluded.metadata,
                updated_at=excluded.updated_at
        """, (category.upper(), key.strip(), val_str, meta_str, now, now))
        await db.commit()
        return True

    async def read_memory(self, category: str, key: str) -> Optional[Dict[str, Any]]:
        await self.init_db()
        db = await self.get_connection()
        cursor = await db.execute(
            "SELECT * FROM memory_records WHERE category = ? AND key = ?",
            (category.upper(), key.strip())
        )
        row = await cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        try:
            res["value"] = json.loads(res["value"])
        except Exception:
            pass
        return res

    async def update_memory(
        self,
        category: str,
        key: str,
        value: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        return await self.create_memory(category, key, value, metadata)

    async def delete_memory(self, category: str, key: str) -> bool:
        await self.init_db()
        db = await self.get_connection()
        cursor = await db.execute(
            "DELETE FROM memory_records WHERE category = ? AND key = ?",
            (category.upper(), key.strip())
        )
        await db.commit()
        return cursor.rowcount > 0

    async def search_memory(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        await self.init_db()
        db = await self.get_connection()
        term = f"%{query.strip()}%"
        if category:
            cursor = await db.execute(
                "SELECT * FROM memory_records WHERE category = ? AND (key LIKE ? OR value LIKE ?) ORDER BY updated_at DESC",
                (category.upper(), term, term)
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM memory_records WHERE key LIKE ? OR value LIKE ? ORDER BY updated_at DESC",
                (term, term)
            )
        rows = await cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            try:
                d["value"] = json.loads(d["value"])
            except Exception:
                pass
            results.append(d)
        return results

    async def list_memory_by_category(self, category: str) -> List[Dict[str, Any]]:
        await self.init_db()
        db = await self.get_connection()
        cursor = await db.execute(
            "SELECT * FROM memory_records WHERE category = ? ORDER BY id DESC",
            (category.upper(),)
        )
        rows = await cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            try:
                d["value"] = json.loads(d["value"])
            except Exception:
                pass
            results.append(d)
        return results

    # --- Study Session Operations (Section 7) ---

    async def log_study_session(
        self,
        subject: str,
        topic: str,
        duration_minutes: int,
        notes: str = "",
        session_type: str = "STUDY",
        score: float = 0.0
    ) -> int:
        await self.init_db()
        now = datetime.now().isoformat()
        db = await self.get_connection()
        cursor = await db.execute(
            """INSERT INTO study_sessions 
               (subject, topic, duration_minutes, created_at, notes, session_type, score) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (subject, topic, duration_minutes, now, notes, session_type, score)
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

    # --- Legacy Facts Operations ---

    async def set_fact(self, category: str, key: str, value: str):
        await self.create_memory(category=category, key=key, value=value)

    async def get_facts(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        if category:
            return await self.list_memory_by_category(category)
        await self.init_db()
        db = await self.get_connection()
        cursor = await db.execute("SELECT * FROM memory_records")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
