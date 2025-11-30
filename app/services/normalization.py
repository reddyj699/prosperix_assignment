from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import logging
from app.models.domain import VendorResponse

logger = logging.getLogger(__name__)

class NormalizationService:
    
    @staticmethod
    def normalize_vendor_a(data: Dict[str, Any]) -> VendorResponse:

        
        cost = data.get("cost", 0)
        qty = data.get("qty", 0)
        availability = data.get("availability")

        price = cost if cost > 0 else None
        stock = qty

        
        return VendorResponse(
            vendor_name="VendorA",
            original_data=data,
            normalized_price=price,
            normalized_stock=stock,
            timestamp=datetime.now(timezone.utc)
        )

    @staticmethod
    def normalize_vendor_b(data: Dict[str, Any]) -> VendorResponse:
        # Vendor B: price_cents/stock
        price_cents = data.get("price_cents", 0)
        stock = data.get("stock", 0)

        price = price_cents / 100.0 if price_cents > 0 else None
        
        return VendorResponse(
            vendor_name="VendorB",
            original_data=data,
            normalized_price=price,
            normalized_stock=stock,
            timestamp=datetime.now(timezone.utc)
        )

    @staticmethod
    def normalize_vendor_c(data: Dict[str, Any]) -> VendorResponse:
        # Vendor C: pricing/inventory_level/available/ts
        pricing = data.get("pricing", 0)
        inventory_level = data.get("inventory_level")
        available = data.get("available")
        ts_str = data.get("ts")

        price = pricing if pricing > 0 else None
        
        # Stock logic
        stock = 0
        if inventory_level is not None:
            stock = inventory_level
        elif available: # inventory=null and status="IN_STOCK" (mapped from available=True)
             stock = 5
        else:
             stock = 0

        # Timestamp parsing
        try:
            timestamp = datetime.fromisoformat(ts_str)
        except (ValueError, TypeError):
            timestamp = datetime.now(timezone.utc) # Fallback

        return VendorResponse(
            vendor_name="VendorC",
            original_data=data,
            normalized_price=price,
            normalized_stock=stock,
            timestamp=timestamp
        )

    @staticmethod
    def is_valid(response: VendorResponse) -> bool:
        # Discard data older than 10 minutes
        if datetime.now(timezone.utc) - response.timestamp > timedelta(minutes=10):
            return False
        return True
