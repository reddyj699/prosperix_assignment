import asyncio
import random
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.models.domain import VendorResponse

logger = logging.getLogger(__name__)

class BaseVendor(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def fetch_product(self, sku: str) -> Dict[str, Any]:
        pass

class VendorA(BaseVendor):
    def __init__(self):
        super().__init__("VendorA")

    async def fetch_product(self, sku: str) -> Dict[str, Any]:
        # Mock implementation
        # Returns cost/qty/availability
        return {
            "cost": round(random.uniform(10.0, 100.0), 2),
            "qty": random.randint(0, 50),
            "availability": random.choice(["YES", "NO", "YES"]),
            "ts": datetime.now(timezone.utc).isoformat()
        }

class VendorB(BaseVendor):
    def __init__(self):
        super().__init__("VendorB")

    async def fetch_product(self, sku: str) -> Dict[str, Any]:
        # Mock implementation
        # Returns price_cents/stock
        return {
            "price_cents": random.randint(1000, 10000),
            "stock": random.randint(0, 50),
            "ts": datetime.now(timezone.utc).isoformat()
        }

class VendorC(BaseVendor):
    def __init__(self):
        super().__init__("VendorC")

    async def fetch_product(self, sku: str) -> Dict[str, Any]:
        # Mock implementation with slow and intermittent failures
        # Returns pricing/inventory_level/available/ts
        
        # Simulate delay
        await asyncio.sleep(random.uniform(0.1, 3.0)) # Up to 3 seconds, might trigger timeout

        # Simulate failure
        if random.random() < 0.3: # 30% failure rate
            raise Exception("Vendor C Connection Error")

        return {
            "pricing": round(random.uniform(10.0, 100.0), 2),
            "inventory_level": random.choice([None, random.randint(0, 50)]),
            "available": random.choice([True, False]),
            "ts": datetime.now(timezone.utc).isoformat()
        }

# Factory or list of vendors
def get_vendors():
    return [VendorA(), VendorB(), VendorC()]
