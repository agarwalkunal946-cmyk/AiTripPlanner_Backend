#!/usr/bin/env python3
"""
Basic test script for Razorpay payment integration (without database)
"""

import json
from datetime import datetime
from config.razorpay_config import (
    RAZORPAY_CONFIG, 
    create_dynamic_order_data, 
    get_dynamic_payment_options,
    get_payment_verification_data
)
from utils.user_utils import (
    format_user_data_for_razorpay,
    create_dynamic_order_notes,
    generate_receipt_id,
    validate_payment_data
)

def test_basic_functionality():
    """Test basic payment functionality without database"""
    
    print("🧪 Testing Basic Razorpay Payment Integration")
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
        print(f"✅ Razorpay Config: {json.dumps(RAZORPAY_CONFIG, indent=2, default=str)}")
        
        # Test 2: User Data Formatting
        print("\n2. Testing User Data Formatting...")
        formatted_user = format_user_data_for_razorpay(user_data)
        print(f"✅ Formatted User Data: {json.dumps(formatted_user, indent=2)}")
        
        # Test 3: Order Notes Creation
        print("\n3. Testing Order Notes Creation...")
        order_notes = create_dynamic_order_notes(trip_data, user_data)
        print(f"✅ Order Notes: {json.dumps(order_notes, indent=2)}")
        
        # Test 4: Receipt ID Generation
        print("\n4. Testing Receipt ID Generation...")
        receipt_id = generate_receipt_id(trip_data["id"], user_data["id"])
        print(f"✅ Receipt ID: {receipt_id}")
        
        # Test 5: Dynamic Order Data
        print("\n5. Testing Dynamic Order Data...")
        order_data = create_dynamic_order_data(trip_data, user_data)
        print(f"✅ Order Data: {json.dumps(order_data, indent=2)}")
        
        # Test 6: Dynamic Payment Options
        print("\n6. Testing Dynamic Payment Options...")
        payment_options = get_dynamic_payment_options(trip_data, "order_test_123", user_data)
        print(f"✅ Payment Options: {json.dumps(payment_options, indent=2)}")
        
        # Test 7: Payment Verification Data
        print("\n7. Testing Payment Verification Data...")
        payment_data = {
            "razorpay_payment_id": "pay_test_123",
            "razorpay_order_id": "order_test_123",
            "razorpay_signature": "test_signature_123"
        }
        verification_data = get_payment_verification_data(payment_data, trip_data, user_data)
        print(f"✅ Verification Data: {json.dumps(verification_data, indent=2)}")
        
        # Test 8: Payment Data Validation
        print("\n8. Testing Payment Data Validation...")
        is_valid = validate_payment_data(verification_data)
        print(f"✅ Payment Data Valid: {is_valid}")
        
        # Test 9: Amount Conversion
        print("\n9. Testing Amount Conversion...")
        amount_inr = trip_data["price"]
        amount_paise = amount_inr * 100
        print(f"✅ Amount in INR: ₹{amount_inr}")
        print(f"✅ Amount in Paise: {amount_paise}")
        
        print("\n🎉 All basic tests completed successfully!")
        print("\n📝 Next Steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up MongoDB connection (optional)")
        print("3. Set environment variables for Razorpay keys")
        print("4. Start the server: python start_server.py")
        print("5. Test the endpoints with actual Razorpay integration")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_functionality() 