from typing import List, Optional
from app.models.domain import VendorResponse

class SelectorService:
    @staticmethod
    def select_best_vendor(vendors: List[VendorResponse]) -> Optional[str]:
        # Filter valid vendors (stock > 0 and price exists)
        valid_vendors = [v for v in vendors if v.normalized_stock > 0 and v.normalized_price is not None]

        if not valid_vendors:
            return None

        # Sort by price ascending
        valid_vendors.sort(key=lambda x: x.normalized_price)

        best_vendor = valid_vendors[0]


        
        lowest_price_vendor = valid_vendors[0]
        
        # Find vendor with highest stock
        highest_stock_vendor = max(valid_vendors, key=lambda x: x.normalized_stock)
        
        if lowest_price_vendor == highest_stock_vendor:
            return lowest_price_vendor.vendor_name
            
        price_diff_percent = (highest_stock_vendor.normalized_price - lowest_price_vendor.normalized_price) / lowest_price_vendor.normalized_price
        
        if price_diff_percent > 0.10:
            return highest_stock_vendor.vendor_name
        else:
            return lowest_price_vendor.vendor_name
