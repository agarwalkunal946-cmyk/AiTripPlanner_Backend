


from fastapi import HTTPException, status
from database import user_collection
from models.user import UserCreate, UserLogin, UserResponse, UserUpdate
from auth.password_handler import get_password_hash, verify_password
from auth.jwt_handler import create_access_token
from bson import ObjectId
from datetime import datetime

async def register_user(user_data: UserCreate):
    # Check if email already exists
    existing_user = await user_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    existing_username = await user_collection.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = get_password_hash(user_data.password)
    new_user = {
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True,
        "profile_picture": None
    }
    result = await user_collection.insert_one(new_user)
    
    # Get the created user for response
    created_user = await user_collection.find_one({"_id": result.inserted_id})
    user_response = UserResponse(
        id=str(created_user["_id"]),
        username=created_user["username"],
        email=created_user["email"],
        full_name=created_user.get("full_name"),
        phone=created_user.get("phone"),
        created_at=created_user["created_at"],
        profile_picture=created_user.get("profile_picture")
    )
    
    access_token = create_access_token(data={"sub": user_data.email})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": user_response,
        "message": "User registered successfully"
    }

async def login_user(user_data: UserLogin):
    user = await user_collection.find_one({"email": user_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login time
    await user_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"updated_at": datetime.utcnow()}}
    )
    
    user_response = UserResponse(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        full_name=user.get("full_name"),
        phone=user.get("phone"),
        created_at=user["created_at"],
        profile_picture=user.get("profile_picture")
    )
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer", "user": user_response}

async def get_user_profile(user_email: str):
    user = await user_collection.find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        full_name=user.get("full_name"),
        phone=user.get("phone"),
        created_at=user["created_at"],
        profile_picture=user.get("profile_picture")
    )

async def update_user_profile(user_email: str, user_update: UserUpdate):
    user = await user_collection.find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if username is being updated and if it's already taken
    if user_update.username and user_update.username != user["username"]:
        existing_username = await user_collection.find_one({"username": user_update.username})
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    # Prepare update data
    update_data = {"updated_at": datetime.utcnow()}
    if user_update.username is not None:
        update_data["username"] = user_update.username
    if user_update.full_name is not None:
        update_data["full_name"] = user_update.full_name
    if user_update.phone is not None:
        update_data["phone"] = user_update.phone
    if user_update.profile_picture is not None:
        update_data["profile_picture"] = user_update.profile_picture
    
    # Update user
    result = await user_collection.update_one(
        {"email": user_email},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="No changes made")
    
    # Return updated user
    updated_user = await user_collection.find_one({"email": user_email})
    return UserResponse(
        id=str(updated_user["_id"]),
        username=updated_user["username"],
        email=updated_user["email"],
        full_name=updated_user.get("full_name"),
        phone=updated_user.get("phone"),
        created_at=updated_user["created_at"],
        profile_picture=updated_user.get("profile_picture")
    )

async def change_password(user_email: str, current_password: str, new_password: str):
    user = await user_collection.find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_password(current_password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    hashed_new_password = get_password_hash(new_password)
    await user_collection.update_one(
        {"email": user_email},
        {"$set": {"hashed_password": hashed_new_password, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Password changed successfully"}