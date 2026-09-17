"""SQLite Database connection manager and helpers for Tamizh JARVIS."""
from typing import Optional
import aiosqlite
from config.settings import get_settings


class DatabaseManager:
    """Manages SQLite connection lifecycle."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = db_path
        else:
            settings = get_settings()
            url = settings.DATABASE_URL
            if "///" in url:
                self.db_path = url.split("///")[-1]
            else:
                self.db_path = "jarvis.db"

    async def get_connection(self) -> aiosqlite.Connection:
        db = await aiosqlite.connect(self.db_path)
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys = ON;")
        return db


_default_db: Optional[DatabaseManager] = None


def get_db_manager(db_path: Optional[str] = None) -> DatabaseManager:
    global _default_db
    if db_path:
        return DatabaseManager(db_path)
    if _default_db is None:
        _default_db = DatabaseManager()
    return _default_db
