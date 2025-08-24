from bson import ObjectId
from fastapi import HTTPException
from database import trip_collection, user_collection
from models.trip import TripCreate, TripInDB, TripResponse, TripUpdate, TripSearch
from datetime import datetime
from typing import List, Optional

async def create_new_trip(trip_data: TripCreate):
    host = await user_collection.find_one({"_id": ObjectId(trip_data.host_id)})
    if not host:
        raise HTTPException(status_code=404, detail="Host user not found")

    trip_dict = trip_data.dict()
    trip_dict["created_at"] = datetime.utcnow()
    trip_dict["updated_at"] = datetime.utcnow()
    trip_dict["is_active"] = True
    trip_dict["status"] = "upcoming"

    new_trip = await trip_collection.insert_one(trip_dict)
    created_trip = await trip_collection.find_one({"_id": new_trip.inserted_id})

    return TripResponse(
        id=str(created_trip["_id"]),
        title=created_trip["title"],
        destination=created_trip["destination"],
        duration_days=created_trip["duration_days"],
        price=created_trip["price"],
        description=created_trip.get("description"),
        itinerary=created_trip.get("itinerary", []),
        max_participants=created_trip.get("max_participants"),
        start_date=created_trip.get("start_date"),
        end_date=created_trip.get("end_date"),
        category=created_trip.get("category"),
        difficulty_level=created_trip.get("difficulty_level"),
        image_url=created_trip.get("image_url"),
        host_id=created_trip["host_id"],
        joined_users=created_trip.get("joined_users", []),
        created_at=created_trip["created_at"],
        status=created_trip["status"],
        current_participants=len(created_trip.get("joined_users", []))
    )

async def get_all_trips(limit: int = 50, skip: int = 0):
    trips = []
    cursor = trip_collection.find({"is_active": True}).skip(skip).limit(limit).sort("created_at", -1)

    async for trip in cursor:
        trips.append(TripResponse(
            id=str(trip["_id"]),
            title=trip["title"],
            destination=trip["destination"],
            duration_days=trip["duration_days"],
            price=trip["price"],
            description=trip.get("description"),
            itinerary=trip.get("itinerary", []),
            max_participants=trip.get("max_participants"),
            start_date=trip.get("start_date"),
            end_date=trip.get("end_date"),
            category=trip.get("category"),
            difficulty_level=trip.get("difficulty_level"),
            image_url=trip.get("image_url"),
            host_id=trip["host_id"],
            joined_users=trip.get("joined_users", []),
            created_at=trip["created_at"],
            status=trip["status"],
            current_participants=len(trip.get("joined_users", []))
        ))
    return trips

async def get_trip_by_id(trip_id: str):
    if not ObjectId.is_valid(trip_id):
        raise HTTPException(status_code=400, detail="Invalid trip ID")

    trip = await trip_collection.find_one({"_id": ObjectId(trip_id), "is_active": True})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    return TripResponse(
        id=str(trip["_id"]),
        title=trip["title"],
        destination=trip["destination"],
        duration_days=trip["duration_days"],
        price=trip["price"],
        description=trip.get("description"),
        itinerary=trip.get("itinerary", []),
        max_participants=trip.get("max_participants"),
        start_date=trip.get("start_date"),
        end_date=trip.get("end_date"),
        category=trip.get("category"),
        difficulty_level=trip.get("difficulty_level"),
        image_url=trip.get("image_url"),
        host_id=trip["host_id"],
        joined_users=trip.get("joined_users", []),
        created_at=trip["created_at"],
        status=trip["status"],
        current_participants=len(trip.get("joined_users", []))
    )

async def update_trip(trip_id: str, trip_update: TripUpdate, user_email: str):
    if not ObjectId.is_valid(trip_id):
        raise HTTPException(status_code=400, detail="Invalid trip ID")

    trip = await trip_collection.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    host = await user_collection.find_one({"email": user_email})
    if not host or str(host["_id"]) != trip["host_id"]:
        raise HTTPException(status_code=403, detail="Only the trip host can update the trip")

    update_data = {"updated_at": datetime.utcnow()}
    update_dict = trip_update.dict(exclude_unset=True)
    update_data.update(update_dict)

    result = await trip_collection.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="No changes made")

    updated_trip = await trip_collection.find_one({"_id": ObjectId(trip_id)})
    return TripResponse(
        id=str(updated_trip["_id"]),
        title=updated_trip["title"],
        destination=updated_trip["destination"],
        duration_days=updated_trip["duration_days"],
        price=updated_trip["price"],
        description=updated_trip.get("description"),
        itinerary=updated_trip.get("itinerary", []),
        max_participants=updated_trip.get("max_participants"),
        start_date=updated_trip.get("start_date"),
        end_date=updated_trip.get("end_date"),
        category=updated_trip.get("category"),
        difficulty_level=updated_trip.get("difficulty_level"),
        image_url=updated_trip.get("image_url"),
        host_id=updated_trip["host_id"],
        joined_users=updated_trip.get("joined_users", []),
        created_at=updated_trip["created_at"],
        status=updated_trip["status"],
        current_participants=len(updated_trip.get("joined_users", []))
    )

async def delete_trip(trip_id: str, user_email: str):
    if not ObjectId.is_valid(trip_id):
        raise HTTPException(status_code=400, detail="Invalid trip ID")

    trip = await trip_collection.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    host = await user_collection.find_one({"email": user_email})
    if not host or str(host["_id"]) != trip["host_id"]:
        raise HTTPException(status_code=403, detail="Only the trip host can delete the trip")

    result = await trip_collection.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Could not delete trip")

    return {"message": "Trip deleted successfully"}

async def join_trip_by_id(trip_id: str, user_email: str):
    if not ObjectId.is_valid(trip_id):
        raise HTTPException(status_code=400, detail="Invalid trip ID")

    user = await user_collection.find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    trip = await trip_collection.find_one({"_id": ObjectId(trip_id), "is_active": True})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if str(user["_id"]) == trip["host_id"]:
        raise HTTPException(status_code=400, detail="Host cannot join their own trip")

    if str(user["_id"]) in trip.get("joined_users", []):
        raise HTTPException(status_code=400, detail="You are already a member of this trip")

    max_participants = trip.get("max_participants")
    current_participants = len(trip.get("joined_users", []))
    if max_participants and current_participants >= max_participants:
        raise HTTPException(status_code=400, detail="Trip is full")

    update_result = await trip_collection.update_one(
        {"_id": ObjectId(trip_id)},
        {"$addToSet": {"joined_users": str(user["_id"])}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Could not join trip")

    return {"message": "Successfully joined the trip"}

async def leave_trip(trip_id: str, user_email: str):
    if not ObjectId.is_valid(trip_id):
        raise HTTPException(status_code=400, detail="Invalid trip ID")

    user = await user_collection.find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    trip = await trip_collection.find_one({"_id": ObjectId(trip_id), "is_active": True})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if str(user["_id"]) not in trip.get("joined_users", []):
        raise HTTPException(status_code=400, detail="You are not a member of this trip")

    update_result = await trip_collection.update_one(
        {"_id": ObjectId(trip_id)},
        {"$pull": {"joined_users": str(user["_id"])}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Could not leave trip")

    return {"message": "Successfully left the trip"}

async def search_trips(search_params: TripSearch, limit: int = 50, skip: int = 0):
    query = {"is_active": True}

    if search_params.destination:
        query["destination"] = {"$regex": search_params.destination, "$options": "i"}

    if search_params.category:
        query["category"] = search_params.category

    if search_params.difficulty_level:
        query["difficulty_level"] = search_params.difficulty_level

    if search_params.min_price is not None or search_params.max_price is not None:
        price_query = {}
        if search_params.min_price is not None:
            price_query["$gte"] = search_params.min_price
        if search_params.max_price is not None:
            price_query["$lte"] = search_params.max_price
        query["price"] = price_query

    if search_params.min_duration is not None or search_params.max_duration is not None:
        duration_query = {}
        if search_params.min_duration is not None:
            duration_query["$gte"] = search_params.min_duration
        if search_params.max_duration is not None:
            duration_query["$lte"] = search_params.max_duration
        query["duration_days"] = duration_query

    if search_params.start_date:
        query["start_date"] = {"$gte": search_params.start_date}

    if search_params.end_date:
        query["end_date"] = {"$lte": search_params.end_date}

    trips = []
    cursor = trip_collection.find(query).skip(skip).limit(limit).sort("created_at", -1)

    async for trip in cursor:
        trips.append(TripResponse(
            id=str(trip["_id"]),
            title=trip["title"],
            destination=trip["destination"],
            duration_days=trip["duration_days"],
            price=trip["price"],
            description=trip.get("description"),
            itinerary=trip.get("itinerary", []),
            max_participants=trip.get("max_participants"),
            start_date=trip.get("start_date"),
            end_date=trip.get("end_date"),
            category=trip.get("category"),
            difficulty_level=trip.get("difficulty_level"),
            image_url=trip.get("image_url"),
            host_id=trip["host_id"],
            joined_users=trip.get("joined_users", []),
            created_at=trip["created_at"],
            status=trip["status"],
            current_participants=len(trip.get("joined_users", []))
        ))

    return trips

async def get_user_trips(user_email: str, trip_type: str = "all"):
    user = await user_collection.find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = str(user["_id"])
    query = {"is_active": True}

    if trip_type == "hosted":
        query["host_id"] = user_id
    elif trip_type == "joined":
        query["joined_users"] = user_id
    elif trip_type == "all":
        query["$or"] = [{"host_id": user_id}, {"joined_users": user_id}]
    else:
        raise HTTPException(status_code=400, detail="Invalid trip type")

    trips = []
    cursor = trip_collection.find(query).sort("created_at", -1)

    async for trip in cursor:
        trips.append(TripResponse(
            id=str(trip["_id"]),
            title=trip["title"],
            destination=trip["destination"],
            duration_days=trip["duration_days"],
            price=trip["price"],
            description=trip.get("description"),
            itinerary=trip.get("itinerary", []),
            max_participants=trip.get("max_participants"),
            start_date=trip.get("start_date"),
            end_date=trip.get("end_date"),
            category=trip.get("category"),
            difficulty_level=trip.get("difficulty_level"),
            image_url=trip.get("image_url"),
            host_id=trip["host_id"],
            joined_users=trip.get("joined_users", []),
            created_at=trip["created_at"],
            status=trip["status"],
            current_participants=len(trip.get("joined_users", []))
        ))

    return trips