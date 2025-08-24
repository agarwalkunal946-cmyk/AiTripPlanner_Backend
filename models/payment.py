from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class OrderCreateRequest(BaseModel):
    amount: int = Field(..., description="Amount in paise (multiply by 100)")
    currency: str = Field(default="INR", description="Currency code")
    receipt: str = Field(..., description="Unique receipt identifier")
    notes: Dict[str, Any] = Field(default_factory=dict, description="Additional notes")

class PaymentVerificationRequest(BaseModel):
    razorpay_payment_id: str = Field(..., description="Razorpay payment ID")
    razorpay_order_id: str = Field(..., description="Razorpay order ID")
    razorpay_signature: str = Field(..., description="Razorpay signature for verification")
    tripId: str = Field(..., description="Trip ID")
    userId: str = Field(..., description="User ID")
    amount: float = Field(..., description="Amount in rupees")
    currency: str = Field(default="INR", description="Currency code")
    verificationDate: str = Field(..., description="Verification timestamp")

class PaymentResponse(BaseModel):
    id: str
    amount: int
    currency: str
    receipt: str
    status: str
    notes: Dict[str, Any]
    created_at: datetime

class PaymentVerificationResponse(BaseModel):
    verified: bool
    payment_id: str
    order_id: str
    amount: float
    currency: str
    trip_id: str
    user_id: str
    status: PaymentStatus
    message: str

class PaymentRecord(BaseModel):
    payment_id: str
    order_id: str
    trip_id: str
    user_id: str
    amount: float
    currency: str
    status: PaymentStatus
    razorpay_payment_id: Optional[str] = None
    razorpay_order_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
    notes: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    verification_date: Optional[datetime] = None 