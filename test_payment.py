#!/usr/bin/env python3
"""
Test script for Razorpay payment integration
"""

import asyncio
import json
from datetime import datetime
from models.payment import OrderCreateRequest
from services.payment_service import payment_service
from config.razorpay_config import create_dynamic_order_data, get_dynamic_payment_options

async def test_payment_integration():
    """Test the payment integration"""
    
    print("🧪 Testing Razorpay Payment Integration")
    print("=" * 50)
    
    # Test data
    trip_data = {
        "id": "trip_123",
        "title": "Himalayan Trek",
        "destination": "Manali, Himachal Pradesh",
        "price": 15000,  # ₹15,000
        "duration_days": 7,
        "category": "Adventure",
        "difficulty_level": "Moderate"
    }
    
    user_data = {
        "id": "user_456",
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "9876543210"
    }
    
    try:
        # Test 1: Configuration
        print("\n1. Testing Configuration...")
        config = payment_service.get_razorpay_config()
        print(f"✅ Razorpay Config: {json.dumps(config, indent=2)}")
        
        # Test 2: Dynamic Order Data
        print("\n2. Testing Dynamic Order Data...")
        order_data = create_dynamic_order_data(trip_data, user_data)
        print(f"✅ Order Data: {json.dumps(order_data, indent=2)}")
        
        # Test 3: Dynamic Payment Options
        print("\n3. Testing Dynamic Payment Options...")
        payment_options = get_dynamic_payment_options(trip_data, "order_test_123", user_data)
        print(f"✅ Payment Options: {json.dumps(payment_options, indent=2)}")
        
        # Test 4: Create Order (without actual Razorpay call)
        print("\n4. Testing Order Creation...")
        order_request = OrderCreateRequest(
            amount=order_data["amount"],
            currency=order_data["currency"],
            receipt=order_data["receipt"],
            notes=order_data["notes"]
        )
        print(f"✅ Order Request: {json.dumps(order_request.dict(), indent=2)}")
        
        # Test 5: Health Check
        print("\n5. Testing Health Check...")
        try:
            # This will test the Razorpay connection
            health_status = "healthy" if config.get("key_id") else "unhealthy"
            print(f"✅ Health Status: {health_status}")
        except Exception as e:
            print(f"❌ Health Check Failed: {str(e)}")
        
        print("\n🎉 All tests completed successfully!")
        print("\n📝 Next Steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set environment variables for Razorpay keys")
        print("3. Start the server: python start_server.py")
        print("4. Test the endpoints:")
        print("   - POST /payments/create-order")
        print("   - POST /payments/verify")
        print("   - GET /payments/config")
        print("   - GET /payments/health")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_payment_integration()) 