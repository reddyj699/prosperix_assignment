from fastapi import APIRouter
from app.decorators.wrappers import validate_api_key,validate_sku,rate_limit
from app.core.redis_clinet import redis_client
from app.adapters.vendors import get_vendors
from app.services.normalization import NormalizationService
from app.services.selector import SelectorService
from app.utils.circuit_breaker import circuit_breaker, CircuitBreakerOpenException
from app.models.domain import ProductResponse, VendorResponse
from datetime import datetime, timezone
import asyncio, time, json, logging

router = APIRouter()
logger = logging.getLogger(__name__)
     # <=== No Depends

async def fetch_vendor_with_retry(vendor, sku: str):
    @circuit_breaker(vendor.name)
    async def _fetch():
        start_time = time.time()
        try:
            for attempt in range(3):
                try:
                    return await asyncio.wait_for(vendor.fetch_product(sku), timeout=2)
                except Exception:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(0.5 * (2 ** attempt))
        finally:
            duration = time.time() - start_time

            # MUST await because Redis is async
            await redis_client.incr(f"metrics:vendor:{vendor.name}:request_count")
            await redis_client.incrbyfloat(f"metrics:vendor:{vendor.name}:latency_sum", duration)

    try:
        result = await _fetch()
        return result, None

    except CircuitBreakerOpenException:
        # MUST await
        await redis_client.incr(f"metrics:vendor:{vendor.name}:circuit_trips")
        return None, "Circuit Open"

    except Exception as e:
        # MUST await
        await redis_client.incr(f"metrics:vendor:{vendor.name}:failures")
        return None, str(e)


@router.get("/products/{sku}", response_model=ProductResponse)
@validate_api_key
@rate_limit
@validate_sku
async def get_product(sku: str, x_api_key: str=None):

    await redis_client.z_incrby("stats:sku_requests", 1, sku)

    cache_key = f"product:{sku}"
    cached = await redis_client.get(cache_key)

    if cached:
        return ProductResponse(**json.loads(cached))

    vendors = get_vendors()
    results = await asyncio.gather(*(fetch_vendor_with_retry(v, sku) for v in vendors))

    normalized = []
    for vendor, (data, error) in zip(vendors, results):
        if error:
            normalized.append(VendorResponse(
                vendor_name=vendor.name,
                original_data={},
                timestamp=datetime.now(timezone.utc),
                error=error
            ))
            continue

        if vendor.name == "VendorA":
            n = NormalizationService.normalize_vendor_a(data)
        elif vendor.name == "VendorB":
            n = NormalizationService.normalize_vendor_b(data)
        elif vendor.name == "VendorC":
            n = NormalizationService.normalize_vendor_c(data)
        else:
            continue

        if NormalizationService.is_valid(n):
            normalized.append(n)

    best_vendor = SelectorService.select_best_vendor(normalized)
    total_stock = sum(v.normalized_stock for v in normalized if v.error is None)
    status_str = "IN_STOCK" if total_stock > 0 else "OUT_OF_STOCK"

    response = ProductResponse(
        sku=sku,
        status=status_str,
        best_vendor=best_vendor,
        vendors=normalized
    )

    await redis_client.set(cache_key, response.model_dump_json(), ttl=120)

    return response
