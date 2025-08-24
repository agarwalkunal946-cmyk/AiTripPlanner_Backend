from fastapi import APIRouter, HTTPException, Depends
from controllers import auth_controller
from models.user import UserCreate, UserLogin, TokenSchema, UserResponse, UserUpdate
from auth.jwt_handler import get_current_user
from pydantic import BaseModel
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/register", response_model=TokenSchema)
async def register(user: UserCreate):
    try:
        logger.info(f"Attempting to register user with email: {user.email}")
        return await auth_controller.register_user(user)
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=TokenSchema)
async def login(user: UserLogin):
    try:
        logger.info(f"Attempting login for user with email: {user.email}")
        return await auth_controller.login_user(user)
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: str = Depends(get_current_user)):
    try:
        logger.info(f"Getting profile for user: {current_user}")
        return await auth_controller.get_user_profile(current_user)
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: str = Depends(get_current_user)
):
    try:
        logger.info(f"Updating profile for user: {current_user}")
        return await auth_controller.update_user_profile(current_user, user_update)
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@router.post("/change-password")
async def change_password(
    password_change: PasswordChangeRequest,
    current_user: str = Depends(get_current_user)
):
    try:
        logger.info(f"Changing password for user: {current_user}")
        return await auth_controller.change_password(
            current_user, 
            password_change.current_password, 
            password_change.new_password
        )
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to change password: {str(e)}")

@router.get("/verify-token")
async def verify_token(current_user: str = Depends(get_current_user)):
    try:
        logger.info(f"Verifying token for user: {current_user}")
        return {"valid": True, "user_email": current_user}
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")