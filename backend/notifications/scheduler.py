"""Notification and scheduled reminder subsystem for Tamizh JARVIS with proactive deduplication."""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiosqlite

logger = logging.getLogger("tamizh_jarvis.notifications")


class NotificationManager:
    """Manages scheduled reminders and study alerts with deduplication."""

    def __init__(self, db_path: str = "jarvis.db"):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    scheduled_for TEXT NOT NULL,
                    status TEXT DEFAULT 'PENDING',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await db.commit()

    async def schedule_notification(
        self,
        title: str,
        message: str,
        scheduled_for: Optional[str] = None
    ) -> Dict[str, Any]:
        """Schedules a notification, deduplicating alerts for identical event/time windows."""
        await self.init_db()
        sched_time = scheduled_for or datetime.now().isoformat()
        day_prefix = sched_time[:10] if len(sched_time) >= 10 else sched_time

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            # Deduplication check: same title or message on the same target date
            cursor = await db.execute(
                """SELECT id, title, message, scheduled_for, status FROM notifications 
                   WHERE status = 'PENDING' AND (title = ? OR message = ?) AND scheduled_for LIKE ?""",
                (title.strip(), message.strip(), f"{day_prefix}%")
            )
            existing = await cursor.fetchone()
            if existing:
                logger.info("Deduplicated notification '%s' (matches notification ID %d)", title, existing["id"])
                return {
                    "id": existing["id"],
                    "title": existing["title"],
                    "message": existing["message"],
                    "scheduled_for": existing["scheduled_for"],
                    "status": "ALREADY_SCHEDULED",
                    "deduplicated": True
                }

            # Insert new notification
            ins_cursor = await db.execute(
                "INSERT INTO notifications (title, message, scheduled_for, status) VALUES (?, ?, ?, 'PENDING')",
                (title.strip(), message.strip(), sched_time)
            )
            await db.commit()
            nid = ins_cursor.lastrowid

        return {
            "id": nid,
            "title": title,
            "message": message,
            "scheduled_for": sched_time,
            "status": "PENDING",
            "deduplicated": False
        }

    async def get_pending_notifications(self) -> List[Dict[str, Any]]:
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT id, title, message, scheduled_for, status, created_at FROM notifications WHERE status = 'PENDING' ORDER BY scheduled_for ASC"
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def dismiss_notification(self, notification_id: int) -> bool:
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "UPDATE notifications SET status = 'DISMISSED' WHERE id = ?",
                (notification_id,)
            )
            await db.commit()
            return cursor.rowcount > 0


_notification_mgr = None


def get_notification_manager(db_path: Optional[str] = None) -> NotificationManager:
    global _notification_mgr
    if db_path:
        return NotificationManager(db_path)
    if _notification_mgr is None:
        _notification_mgr = NotificationManager()
    return _notification_mgr
