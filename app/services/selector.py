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

        # Check for price difference rule
        # "Determine the best vendor by choosing the one with stock > 0 and lowest price, 
        # except when price differs by more than 10%, in which case prioritize higher stock"
        # Wait, "price differs by more than 10%" usually implies if the CHEAPER one is significantly cheaper, we take it.
        # But here it says "prioritize higher stock" if price differs by > 10%.
        # This phrasing is slightly ambiguous.
        # Interpretation:
        # Compare the lowest price vendor (A) with others (B).
        # If B has higher stock than A, and B's price is NOT > 10% higher than A? No.
        # Let's re-read: "lowest price, except when price differs by more than 10%, in which case prioritize higher stock"
        # This likely means: If we have a low price vendor with low stock, and a high price vendor with high stock.
        # If the price difference is small (<= 10%), stick with the low price.
        # If the price difference is large (> 10%), prioritize... wait.
        # Usually, you pay more for stock if the cheap one is risky?
        # Or maybe it means: If the prices are CLOSE (within 10%), prioritize STOCK.
        # "except when price differs by more than 10%" -> If price diff > 10%, do X.
        # If price diff <= 10%, do Y.
        # Standard logic: Lowest price wins.
        # Exception: Price differs > 10% -> Prioritize Higher Stock.
        # This sounds like: If there is a HUGE price gap, ignore price and go for stock? That sounds weird.
        # Maybe it means: "Choose lowest price. UNLESS there is a vendor with higher stock whose price is within 10% of the lowest?"
        # Let's stick to the literal text:
        # "Determine the best vendor by choosing the one with stock > 0 and lowest price, except when price differs by more than 10%, in which case prioritize higher stock"
        
        # Let's try to interpret "price differs by more than 10%".
        # Maybe it compares the candidate with the *next* best?
        # Let's assume we are comparing the absolute lowest price vendor (L) with the highest stock vendor (H).
        # If H.price > L.price * 1.10 (differs by more than 10%), then we prioritize higher stock?
        # That would mean we pay MORE for stock?
        # Or does it mean: If the price difference is SMALL (<= 10%), we prioritize stock?
        # "except when price differs by more than 10%" implies the rule (lowest price) applies when diff <= 10%.
        # So if diff <= 10%, we pick lowest price.
        # If diff > 10%, we prioritize higher stock.
        # This seems backward. Usually, if prices are similar, you pick the better stock.
        
        # Let's assume the user meant: "Choose lowest price. BUT if another vendor has higher stock and the price difference is NOT more than 10% (i.e. it's close), pick the higher stock one."
        # BUT, I must follow the prompt literally if possible, or make a reasonable assumption and document it.
        # Literal: "except when price differs by more than 10%, in which case prioritize higher stock"
        # Case 1: Price diff <= 10%. Rule: Lowest price.
        # Case 2: Price diff > 10%. Rule: Prioritize higher stock.
        # This means if I have Vendor A ($100, Stock 1) and Vendor B ($200, Stock 100).
        # Diff is 100%. > 10%. So I pick Vendor B (Higher stock).
        # If I have Vendor A ($100, Stock 1) and Vendor B ($105, Stock 100).
        # Diff is 5%. <= 10%. So I pick Vendor A (Lowest price).
        # This logic encourages paying a premium for stock, but ONLY if the premium is LARGE? That makes no sense.
        # It usually makes sense to pay a SMALL premium for stock.
        
        # Alternative interpretation:
        # "Choose lowest price (Primary Sort: Price ASC).
        # Exception: If price differs by more than 10%... wait.
        
        # Let's go with the most logical interpretation for a "Availability" service:
        # We want the lowest price.
        # However, if there is a vendor with MUCH higher stock, maybe we prefer them?
        
        # Let's try the "Close Price" interpretation which is common:
        # "Choose lowest price. Except when price differs by LESS than 10% (i.e. comparable), then prioritize higher stock."
        # The prompt says "MORE than 10%".
        
        # Let's assume the prompt is written exactly as intended and implements a specific business rule:
        # Rule:
        # 1. Identify the vendor with the Lowest Price (LP).
        # 2. Identify the vendor with the Highest Stock (HS).
        # 3. If LP == HS, return LP.
        # 4. Calculate price difference percentage: (HS.price - LP.price) / LP.price.
        # 5. If diff > 10% (0.10):
        #    Return HS (Prioritize higher stock).
        # 6. Else:
        #    Return LP (Lowest price).
        
        # Example:
        # A: $100, Stock 1. (LP)
        # B: $200, Stock 10. (HS)
        # Diff: (200-100)/100 = 100% > 10%. Pick B.
        # Result: We pay double for more stock.
        
        # Example 2:
        # A: $100, Stock 1. (LP)
        # B: $105, Stock 10. (HS)
        # Diff: 5% <= 10%. Pick A.
        # Result: We stick with cheap one if price is close.
        
        # This logic seems to penalize "close" prices by sticking to the cheap one, but rewards "expensive" prices by switching to them?
        # That seems counter-intuitive.
        
        # Let's look at the prompt again:
        # "Determine the best vendor by choosing the one with stock > 0 and lowest price, except when price differs by more than 10%, in which case prioritize higher stock"
        
        # Maybe "price differs by more than 10%" refers to the VARIANCE across all vendors?
        
        # Let's assume the user made a typo and meant "LESS than 10%".
        # "Choose lowest price, except when price differs by LESS than 10%, in which case prioritize higher stock."
        # This makes business sense: "If prices are similar, pick the one with more stock."
        
        # HOWEVER, as an AI, I should follow instructions or ask.
        # I will implement the "LESS than 10%" logic as it is the standard "tie-breaker" logic, and add a comment.
        # OR, I can implement the literal instruction and document it.
        # "except when price differs by more than 10%, in which case prioritize higher stock"
        # Maybe it means: If the lowest price is an OUTLIER (too cheap, maybe error?), trust the one with higher stock?
        
        # I will implement a robust selection:
        # Sort by Price ASC.
        # Take the top candidate (Lowest Price).
        # Check against other candidates.
        # If any other candidate has Higher Stock AND Price is within X%?
        
        # Let's stick to the literal prompt but inverted to make sense, or just literal?
        # I'll implement the literal prompt but add a comment that it seems unusual, OR I will assume "differs by LESS than 10%" is what was meant because it's a "Normalization" service.
        # Actually, let's look at the "circuit breaker" and "slow vendor" requirements. This is a resilience test.
        # Maybe the rule is: "If the cheapest vendor is significantly cheaper (>10%) than others, we might suspect it, but we take it? No."
        
        # Let's go with:
        # Primary: Lowest Price.
        # Secondary: Stock.
        # Logic:
        # Find Lowest Price Vendor (V_min).
        # Find Highest Stock Vendor (V_stock).
        # If V_stock.price > V_min.price * 1.10:
        #    # Price differs by more than 10%
        #    return V_stock
        # Else:
        #    return V_min
        
        # This literally implements "except when price differs by more than 10%, in which case prioritize higher stock".
        # I will implement this and document it.
        
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
