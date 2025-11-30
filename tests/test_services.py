import pytest
from app.services.normalization import NormalizationService
from app.services.selector import SelectorService
from app.models.domain import VendorResponse
from datetime import datetime, timezone

def test_normalization_vendor_a():
    data = {"cost": 10.0, "qty": 5, "availability": "YES"}
    resp = NormalizationService.normalize_vendor_a(data)
    assert resp.normalized_price == 10.0
    assert resp.normalized_stock == 5
    assert resp.vendor_name == "VendorA"

def test_normalization_vendor_b():
    data = {"price_cents": 2000, "stock": 10}
    resp = NormalizationService.normalize_vendor_b(data)
    assert resp.normalized_price == 20.0
    assert resp.normalized_stock == 10
    assert resp.vendor_name == "VendorB"

def test_normalization_vendor_c():
    data = {"pricing": 30.0, "inventory_level": None, "available": True, "ts": datetime.now(timezone.utc).isoformat()}
    resp = NormalizationService.normalize_vendor_c(data)
    assert resp.normalized_price == 30.0
    assert resp.normalized_stock == 5 # Rule: inventory=null and available=True -> 5
    assert resp.vendor_name == "VendorC"

def test_selector_lowest_price():
    v1 = VendorResponse(vendor_name="A", original_data={}, normalized_price=10.0, normalized_stock=1, timestamp=datetime.now(timezone.utc))
    v2 = VendorResponse(vendor_name="B", original_data={}, normalized_price=20.0, normalized_stock=100, timestamp=datetime.now(timezone.utc))
    
    # Diff is 100% > 10%. Should pick B (Higher Stock)
    best = SelectorService.select_best_vendor([v1, v2])
    assert best == "B"

def test_selector_close_price():
    v1 = VendorResponse(vendor_name="A", original_data={}, normalized_price=100.0, normalized_stock=1, timestamp=datetime.now(timezone.utc))
    v2 = VendorResponse(vendor_name="B", original_data={}, normalized_price=105.0, normalized_stock=100, timestamp=datetime.now(timezone.utc))
    
    # Diff is 5% <= 10%. Should pick A (Lowest Price)
    best = SelectorService.select_best_vendor([v1, v2])
    assert best == "A"
