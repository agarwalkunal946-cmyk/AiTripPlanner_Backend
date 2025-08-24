from database import chat_collection, user_collection
from bson import ObjectId
from datetime import datetime

async def save_message(trip_id: str, user_id: str, message: str):
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None

    message_doc = {
        "trip_id": trip_id,
        "user_id": user_id,
        "username": user.get("username", "Unknown"),
        "message": message,
        "timestamp": datetime.utcnow()
    }
    result = await chat_collection.insert_one(message_doc)
    
    # Use the inserted_id from the result
    inserted_doc = await chat_collection.find_one({"_id": result.inserted_id})
    
    if inserted_doc:
        inserted_doc["_id"] = str(inserted_doc["_id"])
        if isinstance(inserted_doc["timestamp"], datetime):
            inserted_doc["timestamp"] = inserted_doc["timestamp"].isoformat()
        return inserted_doc
    
    return None

async def get_messages_for_trip(trip_id: str, limit: int = 50):
    messages = []
    cursor = chat_collection.find({"trip_id": trip_id}).sort("timestamp", 1).limit(limit)
    async for message in cursor:
        message["_id"] = str(message["_id"])
        if isinstance(message["timestamp"], datetime):
            message["timestamp"] = message["timestamp"].isoformat()
        messages.append(message)
    return messages