
from app.core.redis_clinet import redis_client
from app.adapters.vendors import get_vendors
from app.services.normalization import NormalizationService
from app.services.selector import SelectorService

from app.models.domain import ProductResponse, VendorResponse
from datetime import datetime, timezone
import asyncio, time, json, logging
from app.api.routes import fetch_vendor_with_retry


logger = logging.getLogger(__name__)

async def start_background_tasks():
    while True:
        try:
            logger.info("Running background tasks...")
            await prewarm_cache()
            await record_metrics()
        except Exception as e:
            logger.error(f"Error in background tasks: {e}")

        # Run every 5 minutes
        await asyncio.sleep(300)

async def prewarm_cache():
    # Get top 10 most requested SKUs
    top_skus = await redis_client.zrevrange("stats:sku_requests", 0, 9)

    if not top_skus:
        return

    logger.info(f"Prewarming cache for SKUs: {top_skus}")

    vendors = get_vendors()

    for sku in top_skus:
        try:
            # -------- FETCH VENDORS --------
            results = await asyncio.gather(
                *(fetch_vendor_with_retry(v, sku) for v in vendors)
            )

            normalized = []

            # -------- NORMALIZE --------
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

            # -------- SELECT BEST VENDOR --------
            best_vendor = SelectorService.select_best_vendor(normalized)
            total_stock = sum(v.normalized_stock for v in normalized if v.error is None)
            status_str = "IN_STOCK" if total_stock > 0 else "OUT_OF_STOCK"

            # -------- BUILD RESPONSE --------
            response = ProductResponse(
                sku=sku,
                status=status_str,
                best_vendor=best_vendor,
                vendors=normalized
            )

            # -------- STORE TO CACHE --------
            cache_key = f"product:{sku}"
            await redis_client.set(cache_key, response.model_dump_json(), ttl=120)

            logger.info(f"Prewarmed cache for SKU {sku}")

        except Exception as e:
            logger.error(f"Error prewarming SKU {sku}: {e}")




async def record_metrics():
    # Log metrics from Redis
    # Example: "metrics:vendor:{name}:failures"
    vendors = ["VendorA", "VendorB", "VendorC"]
    for v in vendors:
        failures = await redis_client.get(f"metrics:vendor:{v}:failures") or 0
        latency = await redis_client.get(f"metrics:vendor:{v}:latency_sum") or 0
        count = await redis_client.get(f"metrics:vendor:{v}:request_count") or 1
        avg_latency = float(latency) / float(count) if int(count) > 0 else 0

        logger.info(f"Metrics for {v}: Failures={failures}, Avg Latency={avg_latency:.4f}s")
