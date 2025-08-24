from fastapi import APIRouter, Depends, HTTPException
from typing import List
from services.chat_service import get_messages_for_trip
from auth.jwt_handler import get_current_user

router = APIRouter()

@router.get("/{trip_id}")
async def get_chat_history(
    trip_id: str,
    current_user: str = Depends(get_current_user)
):
    try:
        messages = await get_messages_for_trip(trip_id)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve messages.")