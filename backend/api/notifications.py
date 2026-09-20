"""Notification management endpoints for scheduled reminders."""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from notifications.scheduler import get_notification_manager

router = APIRouter()


class ScheduleNotificationRequest(BaseModel):
    title: str
    message: str
    scheduled_for: Optional[str] = None


@router.get("")
async def list_pending_notifications():
    """Lists all active and pending scheduled reminders."""
    mgr = get_notification_manager()
    notes = await mgr.get_pending_notifications()
    return {"success": True, "notifications": notes, "count": len(notes)}


@router.post("")
async def schedule_notification(request: ScheduleNotificationRequest):
    """Schedules a new reminder or study alert."""
    title = request.title.strip()
    msg = request.message.strip()
    if not title or not msg:
        raise HTTPException(status_code=400, detail="Title and message are required.")

    mgr = get_notification_manager()
    created = await mgr.schedule_notification(
        title=title,
        message=msg,
        scheduled_for=request.scheduled_for
    )
    return {"success": True, "notification": created, "message": "Notification scheduled successfully."}


@router.post("/{notification_id}/dismiss")
async def dismiss_notification(notification_id: int):
    """Dismisses a notification."""
    mgr = get_notification_manager()
    dismissed = await mgr.dismiss_notification(notification_id)
    if not dismissed:
        raise HTTPException(status_code=404, detail="Notification not found.")
    return {"success": True, "message": f"Notification #{notification_id} dismissed."}
