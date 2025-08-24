from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import List, Dict, Any
import logging
from models.payment import (
    OrderCreateRequest,
    PaymentVerificationRequest,
    PaymentResponse,
    PaymentVerificationResponse
)
# Use mock service for testing (comment out for production)
from services.mock_payment_service import mock_payment_service as payment_service
# from services.payment_service import payment_service  # Uncomment for production
from auth.jwt_handler import verify_token

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

@router.post("/create-order", response_model=PaymentResponse)
async def create_order(
    order_data: OrderCreateRequest,
    token: str = Depends(security)
):
    """
    Create a dynamic Razorpay order for trip booking
    """
    try:
        # Verify JWT token (optional - you can remove this if not using JWT)
        # user_data = verify_token(token.credentials)
        
        logger.info(f"Creating order for trip: {order_data.notes.get('tripId')}")
        
        # Create order using payment service
        order_response = await payment_service.create_dynamic_order(order_data)
        
        logger.info(f"Order created successfully: {order_response.id}")
        
        return order_response
        
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

@router.post("/verify", response_model=PaymentVerificationResponse)
async def verify_payment(
    verification_data: PaymentVerificationRequest,
    token: str = Depends(security)
):
    """
    Verify payment signature and update payment status
    """
    try:
        # Verify JWT token (optional - you can remove this if not using JWT)
        # user_data = verify_token(token.credentials)
        
        logger.info(f"Verifying payment: {verification_data.razorpay_payment_id}")
        
        # Verify payment using payment service
        verification_response = await payment_service.verify_payment(verification_data)
        
        if verification_response.verified:
            logger.info(f"Payment verified successfully: {verification_response.payment_id}")
        else:
            logger.warning(f"Payment verification failed: {verification_response.message}")
        
        return verification_response
        
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to verify payment: {str(e)}")

@router.get("/history/{user_id}", response_model=List[Dict[str, Any]])
async def get_payment_history(
    user_id: str,
    limit: int = 10,
    token: str = Depends(security)
):
    """
    Get payment history for a user
    """
    try:
        # Verify JWT token (optional - you can remove this if not using JWT)
        # user_data = verify_token(token.credentials)
        
        logger.info(f"Fetching payment history for user: {user_id}")
        
        # Get payment history using payment service
        payments = await payment_service.get_payment_history(user_id, limit)
        
        return payments
        
    except Exception as e:
        logger.error(f"Error fetching payment history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch payment history: {str(e)}")

@router.get("/payment/{payment_id}", response_model=Dict[str, Any])
async def get_payment_details(
    payment_id: str,
    token: str = Depends(security)
):
    """
    Get payment details by payment ID
    """
    try:
        # Verify JWT token (optional - you can remove this if not using JWT)
        # user_data = verify_token(token.credentials)
        
        logger.info(f"Fetching payment details: {payment_id}")
        
        # Get payment details using payment service
        payment = await payment_service.get_payment_by_id(payment_id)
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        return payment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching payment details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch payment details: {str(e)}")

@router.get("/config")
async def get_razorpay_config():
    """
    Get Razorpay configuration for frontend
    """
    try:
        config = payment_service.get_razorpay_config()
        return config
        
    except Exception as e:
        logger.error(f"Error fetching Razorpay config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Razorpay config: {str(e)}")

@router.post("/webhook")
async def razorpay_webhook(request: Dict[str, Any]):
    """
    Handle Razorpay webhook events
    """
    try:
        logger.info(f"Received webhook: {request}")
        
        # Extract webhook data
        event_type = request.get("event")
        payload = request.get("payload", {})
        
        if event_type == "payment.captured":
            # Handle successful payment
            payment_data = payload.get("payment", {})
            order_data = payload.get("order", {})
            
            logger.info(f"Payment captured: {payment_data.get('id')}")
            
            # You can add additional webhook processing logic here
            # For example, sending confirmation emails, updating trip status, etc.
            
        elif event_type == "payment.failed":
            # Handle failed payment
            payment_data = payload.get("payment", {})
            logger.warning(f"Payment failed: {payment_data.get('id')}")
            
        return {"status": "success", "message": "Webhook processed"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process webhook: {str(e)}")

@router.get("/health")
async def payment_health_check():
    """
    Health check endpoint for payment service
    """
    try:
        # Test Razorpay connection
        config = payment_service.get_razorpay_config()
        
        return {
            "status": "healthy",
            "service": "payment",
            "razorpay_configured": bool(config.get("key_id")),
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Payment service health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Payment service unhealthy") 