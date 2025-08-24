from typing import Dict, Any, Optional
import json

def format_user_data_for_razorpay(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format user data for Razorpay payment options
    """
    return {
        "id": user_data.get("id", "anonymous"),
        "name": user_data.get("name", "User Name"),
        "email": user_data.get("email", "user@example.com"),
        "phone": user_data.get("phone", "9999999999"),
    }

def create_dynamic_order_notes(trip_data: Dict[str, Any], user_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create dynamic notes for Razorpay order
    """
    notes = {
        "tripId": trip_data.get("id", ""),
        "tripTitle": trip_data.get("title", ""),
        "destination": trip_data.get("destination", ""),
        "duration": trip_data.get("duration_days", 0),
        "category": trip_data.get("category", "Adventure"),
        "difficulty": trip_data.get("difficulty_level", "Moderate"),
        "bookingDate": "2024-01-01T00:00:00Z",  # This will be updated with actual date
    }
    
    if user_data:
        notes.update({
            "userId": user_data.get("id", "anonymous"),
            "userEmail": user_data.get("email", "user@example.com"),
            "userName": user_data.get("name", "User Name"),
        })
    
    return notes

def generate_receipt_id(trip_id: str, user_id: str = "anonymous") -> str:
    """
    Generate a unique receipt ID for Razorpay order
    """
    import time
    import random
    import string
    
    timestamp = int(time.time())
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    return f"trip_{trip_id}_{user_id}_{timestamp}_{random_suffix}"

def validate_payment_data(payment_data: Dict[str, Any]) -> bool:
    """
    Validate payment data received from frontend
    """
    required_fields = [
        "razorpay_payment_id",
        "razorpay_order_id", 
        "razorpay_signature",
        "tripId",
        "userId",
        "amount"
    ]
    
    for field in required_fields:
        if field not in payment_data or not payment_data[field]:
            return False
    
    return True

def format_payment_response(payment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format payment response for frontend
    """
    return {
        "payment_id": payment_data.get("razorpay_payment_id"),
        "order_id": payment_data.get("razorpay_order_id"),
        "amount": payment_data.get("amount"),
        "currency": payment_data.get("currency", "INR"),
        "status": "success",
        "trip_id": payment_data.get("tripId"),
        "user_id": payment_data.get("userId"),
        "timestamp": "2024-01-01T00:00:00Z"
    } 