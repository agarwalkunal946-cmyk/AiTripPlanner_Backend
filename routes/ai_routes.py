from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from services import ai_planner_service
# Assuming you have a get_current_user dependency for authentication
# from auth.jwt_handler import get_current_user 

router = APIRouter()

class AIPlannerRequest(BaseModel):
    destination: str
    duration_days: int
    budget: Optional[str] = "moderate"
    interests: Optional[List[str]] = []

@router.post("/plan-trip")
async def plan_trip_with_ai(
    request: AIPlannerRequest,
    # current_user: str = Depends(get_current_user) # Uncomment if you have auth
):
    try:
        plan = await ai_planner_service.generate_trip_plan(request.dict())
        return plan
    except HTTPException as e:
        # Re-raise HTTPException from the service layer directly
        raise e
    except Exception as e:
        print(e,'eee')
        # Catch any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"An unexpected error occurred on the server: {e}"
        )