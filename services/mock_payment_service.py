import hashlib
import hmac
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

class MockPaymentService:
    def __init__(self):
        # Initialize with test configuration
        from config.razorpay_config import RAZORPAY_CONFIG
        self.key_id = RAZORPAY_CONFIG["KEY_ID"]
        self.key_secret = RAZORPAY_CONFIG["KEY_SECRET"]
        
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
        
        logger.info(f"Mock payment service initialized with key_id: {self.key_id[:10]}...")
    
    async def create_dynamic_order(self, order_data: OrderCreateRequest) -> PaymentResponse:
        """
        Create a mock order (for testing without actual Razorpay)
        """
        try:
            # Generate mock order ID
            mock_order_id = f"order_mock_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            logger.info(f"Creating mock order: {mock_order_id}")
            
            # Store order in database
            if self.orders_collection is not None:
                order_record = {
                    "order_id": mock_order_id,
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
                    payment_id=f"pay_mock_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{order_data.notes.get('tripId', 'unknown')}",
                    order_id=mock_order_id,
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
            
            logger.info(f"Mock order created successfully: {mock_order_id}")
            
            return PaymentResponse(
                id=mock_order_id,
                amount=order_data.amount,
                currency=order_data.currency,
                receipt=order_data.receipt,
                status="created",
                notes=order_data.notes,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error creating mock order: {str(e)}")
            raise Exception(f"Failed to create mock order: {str(e)}")
    
    async def verify_payment(self, verification_data: PaymentVerificationRequest) -> PaymentVerificationResponse:
        """
        Mock payment verification (for testing)
        """
        try:
            logger.info(f"Mock payment verification: {verification_data.razorpay_payment_id}")
            
            # For mock testing, we'll always return success
            # In real implementation, this would verify the signature
            
            # Find and update payment record
            if self.payments_collection is None:
                logger.warning("Database not available - skipping payment verification update")
                return PaymentVerificationResponse(
                    verified=True,  # Mock success
                    payment_id=verification_data.razorpay_payment_id,
                    order_id=verification_data.razorpay_order_id,
                    amount=verification_data.amount,
                    currency=verification_data.currency,
                    trip_id=verification_data.tripId,
                    user_id=verification_data.userId,
                    status=PaymentStatus.SUCCESS,
                    message="Mock payment verified successfully"
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
            
            # Update order status
            if self.orders_collection is not None:
                await self.orders_collection.update_one(
                    {"order_id": verification_data.razorpay_order_id},
                    {"$set": {"status": "paid", "updated_at": datetime.utcnow()}}
                )
            else:
                logger.warning("Database not available - skipping order status update")
            
            logger.info(f"Mock payment verified successfully: {verification_data.razorpay_payment_id}")
            
            return PaymentVerificationResponse(
                verified=True,
                payment_id=verification_data.razorpay_payment_id,
                order_id=verification_data.razorpay_order_id,
                amount=verification_data.amount,
                currency=verification_data.currency,
                trip_id=verification_data.tripId,
                user_id=verification_data.userId,
                status=PaymentStatus.SUCCESS,
                message="Mock payment verified successfully"
            )
            
        except Exception as e:
            logger.error(f"Error verifying mock payment: {str(e)}")
            return PaymentVerificationResponse(
                verified=False,
                payment_id="",
                order_id=verification_data.razorpay_order_id,
                amount=verification_data.amount,
                currency=verification_data.currency,
                trip_id=verification_data.tripId,
                user_id=verification_data.userId,
                status=PaymentStatus.FAILED,
                message=f"Mock payment verification error: {str(e)}"
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
mock_payment_service = MockPaymentService() 