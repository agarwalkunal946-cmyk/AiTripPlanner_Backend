from database import user_collection
from auth.jwt_handler import verify_token
from bson import ObjectId

async def get_user_from_token(token: str):
    payload = verify_token(token)
    if not payload or not payload.get("sub"):
        return None
    
    user = await user_collection.find_one({"email": payload["sub"]})
    if user:
        # The frontend expects 'id' not '_id' for the user object check
        user['id'] = str(user['_id'])
    return user