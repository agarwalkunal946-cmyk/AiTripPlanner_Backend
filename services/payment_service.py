import razorpay
import hashlib
import hmac
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from models.payment import (
    OrderCreateRequest, 
    PaymentVerificationRequest, 
    PaymentResponse, 
    PaymentVerificationResponse,
    PaymentRecord,
    PaymentStatus
)
from database import get_database
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        # Initialize Razorpay client with environment variables
        from config.razorpay_config import RAZORPAY_CONFIG
        self.key_id = RAZORPAY_CONFIG["KEY_ID"]
        self.key_secret = RAZORPAY_CONFIG["KEY_SECRET"]
        
        # Initialize Razorpay client
        self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
        
        # Get database connection
        try:
            self.db = get_database()
            if self.db is not None:
                self.payments_collection = self.db.payments
                self.orders_collection = self.db.orders
            else:
                self.payments_collection = None
                self.orders_collection = None
        except Exception as e:
            logger.warning(f"Database connection not available: {str(e)}")
            self.db = None
            self.payments_collection = None
            self.orders_collection = None
        
        logger.info(f"Payment service initialized with key_id: {self.key_id[:10]}...")
    
    async def create_dynamic_order(self, order_data: OrderCreateRequest) -> PaymentResponse:
        """
        Create a dynamic order with Razorpay based on trip and user data
        """
        try:
            # Prepare order data for Razorpay
            razorpay_order_data = {
                "amount": order_data.amount,
                "currency": order_data.currency,
                "receipt": order_data.receipt,
                "notes": order_data.notes
            }
            
            logger.info(f"Creating Razorpay order with data: {razorpay_order_data}")
            
            # Create order with Razorpay
            razorpay_order = self.client.order.create(data=razorpay_order_data)
            
            # Store order in database
            if self.orders_collection is not None:
                order_record = {
                    "order_id": razorpay_order["id"],
                    "amount": order_data.amount,
                    "currency": order_data.currency,
                    "receipt": order_data.receipt,
                    "status": "created",
                    "notes": order_data.notes,
                    "trip_id": order_data.notes.get("tripId"),
                    "user_id": order_data.notes.get("userId"),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                await self.orders_collection.insert_one(order_record)
            else:
                logger.warning("Database not available - skipping order storage")
            
            # Create payment record
            if self.payments_collection is not None:
                payment_record = PaymentRecord(
                    payment_id=f"pay_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{order_data.notes.get('tripId', 'unknown')}",
                    order_id=razorpay_order["id"],
                    trip_id=order_data.notes.get("tripId", ""),
                    user_id=order_data.notes.get("userId", ""),
                    amount=order_data.amount / 100,  # Convert from paise to rupees
                    currency=order_data.currency,
                    status=PaymentStatus.PENDING,
                    notes=order_data.notes,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                await self.payments_collection.insert_one(payment_record.dict())
            else:
                logger.warning("Database not available - skipping payment record storage")
            
            logger.info(f"Order created successfully: {razorpay_order['id']}")
            
            return PaymentResponse(
                id=razorpay_order["id"],
                amount=razorpay_order["amount"],
                currency=razorpay_order["currency"],
                receipt=razorpay_order["receipt"],
                status=razorpay_order["status"],
                notes=order_data.notes,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            raise Exception(f"Failed to create order: {str(e)}")
    
    async def verify_payment(self, verification_data: PaymentVerificationRequest) -> PaymentVerificationResponse:
        """
        Verify payment signature and update payment status
        """
        try:
            # Prepare data for signature verification
            data = f"{verification_data.razorpay_order_id}|{verification_data.razorpay_payment_id}"
            
            # Generate expected signature
            expected_signature = hmac.new(
                self.key_secret.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Verify signature
            if not hmac.compare_digest(expected_signature, verification_data.razorpay_signature):
                logger.warning(f"Signature verification failed for payment: {verification_data.razorpay_payment_id}")
                return PaymentVerificationResponse(
                    verified=False,
                    payment_id="",
                    order_id=verification_data.razorpay_order_id,
                    amount=verification_data.amount,
                    currency=verification_data.currency,
                    trip_id=verification_data.tripId,
                    user_id=verification_data.userId,
                    status=PaymentStatus.FAILED,
                    message="Payment signature verification failed"
                )
            
            # Find and update payment record
            if self.payments_collection is None:
                logger.warning("Database not available - skipping payment verification update")
                return PaymentVerificationResponse(
                    verified=False,
                    payment_id="",
                    order_id=verification_data.razorpay_order_id,
                    amount=verification_data.amount,
                    currency=verification_data.currency,
                    trip_id=verification_data.tripId,
                    user_id=verification_data.userId,
                    status=PaymentStatus.FAILED,
                    message="Database not available"
                )
            
            payment_filter = {
                "order_id": verification_data.razorpay_order_id,
                "trip_id": verification_data.tripId,
                "user_id": verification_data.userId
            }
            
            payment_update = {
                "$set": {
                    "razorpay_payment_id": verification_data.razorpay_payment_id,
                    "razorpay_signature": verification_data.razorpay_signature,
                    "status": PaymentStatus.SUCCESS,
                    "verification_date": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
            
            result = await self.payments_collection.update_one(payment_filter, payment_update)
            
            if result.modified_count == 0:
                logger.warning(f"No payment record found for order: {verification_data.razorpay_order_id}")
                return PaymentVerificationResponse(
                    verified=False,
                    payment_id="",
                    order_id=verification_data.razorpay_order_id,
                    amount=verification_data.amount,
                    currency=verification_data.currency,
                    trip_id=verification_data.tripId,
                    user_id=verification_data.userId,
                    status=PaymentStatus.FAILED,
                    message="Payment record not found"
                )
            
            # Update order status
            if self.orders_collection is not None:
                await self.orders_collection.update_one(
                    {"order_id": verification_data.razorpay_order_id},
                    {"$set": {"status": "paid", "updated_at": datetime.utcnow()}}
                )
            else:
                logger.warning("Database not available - skipping order status update")
            
            logger.info(f"Payment verified successfully: {verification_data.razorpay_payment_id}")
            
            return PaymentVerificationResponse(
                verified=True,
                payment_id=verification_data.razorpay_payment_id,
                order_id=verification_data.razorpay_order_id,
                amount=verification_data.amount,
                currency=verification_data.currency,
                trip_id=verification_data.tripId,
                user_id=verification_data.userId,
                status=PaymentStatus.SUCCESS,
                message="Payment verified successfully"
            )
            
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            return PaymentVerificationResponse(
                verified=False,
                payment_id="",
                order_id=verification_data.razorpay_order_id,
                amount=verification_data.amount,
                currency=verification_data.currency,
                trip_id=verification_data.tripId,
                user_id=verification_data.userId,
                status=PaymentStatus.FAILED,
                message=f"Payment verification error: {str(e)}"
            )
    
    async def get_payment_history(self, user_id: str, limit: int = 10) -> list:
        """
        Get payment history for a user
        """
        try:
            if self.payments_collection is None:
                logger.warning("Database not available - returning empty payment history")
                return []
                
            cursor = self.payments_collection.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(limit)
            
            payments = await cursor.to_list(length=limit)
            return payments
            
        except Exception as e:
            logger.error(f"Error fetching payment history: {str(e)}")
            return []
    
    async def get_payment_by_id(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get payment details by payment ID
        """
        try:
            if self.payments_collection is None:
                logger.warning("Database not available - returning None for payment details")
                return None
                
            payment = await self.payments_collection.find_one({"payment_id": payment_id})
            return payment
            
        except Exception as e:
            logger.error(f"Error fetching payment: {str(e)}")
            return None
    
    def get_razorpay_config(self) -> Dict[str, Any]:
        """
        Get Razorpay configuration for frontend
        """
        from config.razorpay_config import RAZORPAY_CONFIG
        return {
            "key_id": self.key_id,
            "currency": RAZORPAY_CONFIG["CURRENCY"],
            "app_name": RAZORPAY_CONFIG["APP_NAME"],
            "theme_color": RAZORPAY_CONFIG["THEME_COLOR"],
            "payment_options": RAZORPAY_CONFIG["PAYMENT_OPTIONS"]
        }

# Create global instance
payment_service = PaymentService() 