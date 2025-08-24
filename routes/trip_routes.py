from fastapi import APIRouter, HTTPException, Depends, Query, Request, File, UploadFile, Form
from controllers import trip_controller
from models.trip import TripBase, TripCreate, TripResponse, TripUpdate, TripSearch
from auth.jwt_handler import get_current_user
from typing import List, Optional
from pydantic import BaseModel
from database import user_collection
from bson import ObjectId
from datetime import datetime
import os
import uuid
import shutil

router = APIRouter()

IMAGE_UPLOAD_DIR = "static/images"
os.makedirs(IMAGE_UPLOAD_DIR, exist_ok=True)

class TripJoinRequest(BaseModel):
    trip_id: str

@router.post("/", response_model=TripResponse)
async def create_trip(
    request: Request,
    title: str = Form(...),
    destination: str = Form(...),
    duration_days: str = Form(...),
    price: str = Form(...),
    category: str = Form(...),
    description: Optional[str] = Form(None),
    difficulty_level: Optional[str] = Form(None),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user_email: str = Depends(get_current_user)
):
    try:
        user = await user_collection.find_one({"email": current_user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            duration_days_int = int(duration_days)
            price_float = float(price)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid duration_days or price format")

        start_date_obj = None
        end_date_obj = None
        
        if start_date:
            try:
                if len(start_date) == 10:
                    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                else:
                    start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=422, detail="Invalid start_date format. Use YYYY-MM-DD")

        if end_date:
            try:
                if len(end_date) == 10:
                    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                else:
                    end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=422, detail="Invalid end_date format. Use YYYY-MM-DD")

        image_url = None
        if image:
            file_extension = os.path.splitext(image.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(IMAGE_UPLOAD_DIR, unique_filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            base_url = str(request.base_url).rstrip('/')
            
            if 'ngrok' in base_url and base_url.startswith('http://'):
                base_url = base_url.replace('http://', 'https://', 1)

            image_url = f"{base_url}/{file_path}"
            
        trip_data_dict = {
            "title": title,
            "destination": destination,
            "description": description,
            "duration_days": duration_days_int,
            "price": price_float,
            "category": category,
            "difficulty_level": difficulty_level,
            "start_date": start_date_obj,
            "end_date": end_date_obj,
            "image_url": image_url,
        }
        
        trip_to_create = TripCreate(
            **trip_data_dict,
            host_id=str(user["_id"])
        )

        return await trip_controller.create_new_trip(trip_to_create)
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create trip: {str(e)}")

@router.get("/", response_model=List[TripResponse])
async def get_trips(
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    try:
        return await trip_controller.get_all_trips(limit=limit, skip=skip)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trips: {str(e)}")

@router.get("/search", response_model=List[TripResponse])
async def search_trips(
    destination: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    min_duration: Optional[int] = Query(None, ge=1),
    max_duration: Optional[int] = Query(None, ge=1),
    difficulty_level: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    try:
        search_params = TripSearch(
            destination=destination,
            category=category,
            min_price=min_price,
            max_price=max_price,
            min_duration=min_duration,
            max_duration=max_duration,
            difficulty_level=difficulty_level
        )
        return await trip_controller.search_trips(search_params, limit=limit, skip=skip)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search trips: {str(e)}")

@router.get("/my-trips", response_model=List[TripResponse])
async def get_my_trips(
    trip_type: str = Query("all", pattern="^(all|hosted|joined)$"),
    current_user: str = Depends(get_current_user)
):
    try:
        return await trip_controller.get_user_trips(current_user, trip_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user trips: {str(e)}")

@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: str):
    try:
        return await trip_controller.get_trip_by_id(trip_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trip: {str(e)}")

@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: str,
    trip_update: TripUpdate,
    current_user: str = Depends(get_current_user)
):
    try:
        return await trip_controller.update_trip(trip_id, trip_update, current_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update trip: {str(e)}")

@router.delete("/{trip_id}", status_code=204)
async def delete_trip(
    trip_id: str,
    current_user: str = Depends(get_current_user)
):
    try:
        result = await trip_controller.delete_trip(trip_id, current_user)
        if not result:
            raise HTTPException(status_code=404, detail="Trip not found or user not authorized")
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete trip: {str(e)}")

@router.post("/{trip_id}/join", status_code=200)
async def join_trip(
    trip_id: str,
    current_user: str = Depends(get_current_user)
):
    try:
        return await trip_controller.join_trip_by_id(trip_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to join trip: {str(e)}")

@router.post("/{trip_id}/leave", status_code=200)
async def leave_trip(
    trip_id: str,
    current_user: str = Depends(get_current_user)
):
    try:
        return await trip_controller.leave_trip(trip_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to leave trip: {str(e)}")

@router.get("/info/categories")
async def get_categories():
    return {
        "categories": [
            "Adventure", "Cultural", "Relaxation", "Business", "Educational",
            "Photography", "Food & Wine", "Wildlife", "Historical", "Beach",
            "Mountain", "City", "Rural", "Solo", "Family", "Romantic"
        ]
    }

@router.get("/info/difficulty-levels")
async def get_difficulty_levels():
    return {
        "difficulty_levels": [
            "Easy", "Moderate", "Challenging", "Difficult", "Expert"
        ]
    }