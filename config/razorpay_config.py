import os
from typing import Dict, Any

# Razorpay Configuration
RAZORPAY_CONFIG = {
    # Test keys - Replace with your actual keys
    "KEY_ID": os.getenv('RAZORPAY_KEY_ID', 'rzp_test_0ZPYiHpjj69JAD'),
    "KEY_SECRET": os.getenv('RAZORPAY_KEY_SECRET', 'vjVn6mgfh9jO0dxIDGE8YX5E'),
    
    # Production keys - Uncomment when going live
    # "KEY_ID": os.getenv('RAZORPAY_LIVE_KEY_ID', 'rzp_live_YOUR_LIVE_KEY_ID'),
    # "KEY_SECRET": os.getenv('RAZORPAY_LIVE_KEY_SECRET', 'YOUR_LIVE_KEY_SECRET'),
    
    # App configuration
    "APP_NAME": "AI Trip Planner",
    "APP_LOGO": "https://your-app-logo.png",  # Replace with your app logo URL
    "CURRENCY": "INR",
    "THEME_COLOR": "#00C9A7",
    
    # Payment options
    "PAYMENT_OPTIONS": {
        "netbanking": True,
        "card": True,
        "upi": True,
        "wallet": True,
    },
}

def get_dynamic_payment_options(trip_data: Dict[str, Any], order_id: str, user_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate dynamic payment options with trip data
    """
    # Generate dynamic receipt ID
    from utils.user_utils import generate_receipt_id
    receipt_id = generate_receipt_id(trip_data.get("id", ""), user_data.get("id", "anonymous") if user_data else "anonymous")
    
    # Dynamic description based on trip details
    description = f"Payment for {trip_data.get('title', 'Trip')} - {trip_data.get('destination', 'Destination')}"
    
    # Dynamic prefill data from user profile or use defaults
    prefill = user_data and {
        "email": user_data.get("email", "user@example.com"),
        "contact": user_data.get("phone", "9999999999"),
        "name": user_data.get("name", "User Name"),
    } or {
        "email": "user@example.com",
        "contact": "9999999999",
        "name": "User Name",
    }

    return {
        "description": description,
        "image": RAZORPAY_CONFIG["APP_LOGO"],
        "currency": RAZORPAY_CONFIG["CURRENCY"],
        "key": RAZORPAY_CONFIG["KEY_ID"],
        "amount": trip_data.get("price", 0) * 100,  # Convert to paise
        "name": RAZORPAY_CONFIG["APP_NAME"],
        "order_id": order_id,
        "receipt": receipt_id,
        "prefill": prefill,
        "theme": {"color": RAZORPAY_CONFIG["THEME_COLOR"]},
        "notes": {
            "tripId": trip_data.get("id", ""),
            "tripTitle": trip_data.get("title", ""),
            "destination": trip_data.get("destination", ""),
            "duration": trip_data.get("duration_days", 0),
            "category": trip_data.get("category", "Adventure"),
            "difficulty": trip_data.get("difficulty_level", "Moderate"),
            "bookingDate": "2024-01-01T00:00:00Z",
        },
        **RAZORPAY_CONFIG["PAYMENT_OPTIONS"]
    }

def create_dynamic_order_data(trip_data: Dict[str, Any], user_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create dynamic order data for backend
    """
    from utils.user_utils import generate_receipt_id, create_dynamic_order_notes
    
    return {
        "amount": trip_data.get("price", 0) * 100,  # Convert to paise
        "currency": RAZORPAY_CONFIG["CURRENCY"],
        "receipt": generate_receipt_id(trip_data.get("id", ""), user_data.get("id", "anonymous") if user_data else "anonymous"),
        "notes": create_dynamic_order_notes(trip_data, user_data)
    }

def get_payment_verification_data(payment_data: Dict[str, Any], trip_data: Dict[str, Any], user_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get payment verification data
    """
    return {
        "razorpay_payment_id": payment_data.get("razorpay_payment_id"),
        "razorpay_order_id": payment_data.get("razorpay_order_id"),
        "razorpay_signature": payment_data.get("razorpay_signature"),
        "tripId": trip_data.get("id", ""),
        "userId": user_data.get("id", "anonymous") if user_data else "anonymous",
        "amount": trip_data.get("price", 0),
        "currency": RAZORPAY_CONFIG["CURRENCY"],
        "verificationDate": "2024-01-01T00:00:00Z",
    }

# Legacy function for backward compatibility
def get_payment_options(amount: float, order_id: str, description: str) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility
    """
    return {
        "description": description,
        "image": RAZORPAY_CONFIG["APP_LOGO"],
        "currency": RAZORPAY_CONFIG["CURRENCY"],
        "key": RAZORPAY_CONFIG["KEY_ID"],
        "amount": amount * 100,  # Convert to paise
        "name": RAZORPAY_CONFIG["APP_NAME"],
        "order_id": order_id,
        "prefill": {
            "email": "user@example.com",
            "contact": "9999999999",
            "name": "User Name",
        },
        "theme": {"color": RAZORPAY_CONFIG["THEME_COLOR"]},
        **RAZORPAY_CONFIG["PAYMENT_OPTIONS"]
    } 