#!/usr/bin/env python3
"""
Test script to verify payment endpoint works
"""

import requests
import json

def test_payment_endpoint():
    """Test the payment endpoint"""
    
    print("🧪 Testing Payment Endpoint")
    print("=" * 30)
    
    base_url = "http://localhost:8000"
    
    # Test data
    order_data = {
        "amount": 1500000,  # ₹15,000 in paise
        "currency": "INR",
        "receipt": "test_receipt_123",
        "notes": {
            "tripId": "trip_123",
            "tripTitle": "Himalayan Trek",
            "destination": "Manali, Himachal Pradesh",
            "duration": 7,
            "category": "Adventure",
            "difficulty": "Moderate",
            "userId": "user_456",
            "userEmail": "john@example.com",
            "userName": "John Doe",
            "bookingDate": "2024-01-01T00:00:00Z"
        }
    }
    
    try:
        # Test 1: Health check
        print("\n1. Testing Health Check...")
        response = requests.get(f"{base_url}/payments/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test 2: Get config
        print("\n2. Testing Config...")
        response = requests.get(f"{base_url}/payments/config")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test 3: Create order
        print("\n3. Testing Create Order...")
        response = requests.post(
            f"{base_url}/payments/create-order",
            json=order_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
        
        print("\n✅ Endpoint tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running:")
        print("   python start_server.py")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_payment_endpoint() 