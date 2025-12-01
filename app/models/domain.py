from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class VendorResponse(BaseModel):
    vendor_name: str
    original_data: dict
    normalized_price: Optional[float] = None
    normalized_stock: int = 0
    timestamp: datetime
    error: Optional[str] = None

class ProductResponse(BaseModel):
    sku: str
    status: str
    best_vendor: Optional[str] = None
    vendors: List[VendorResponse]

# Vendor Specific Models (for validation if needed, but we deal with raw dicts mostly)
# We will just use these for documentation or strict parsing if we want to be very type safe internally.

class VendorAData(BaseModel):
    cost: float
    qty: int
    availability: str # "YES", "NO"
    ts:str

class VendorBData(BaseModel):
    price_cents: int
    stock: int
    ts:str

class VendorCData(BaseModel):
    pricing: float
    inventory_level: Optional[int]
    available: bool
    ts: str # ISO format
