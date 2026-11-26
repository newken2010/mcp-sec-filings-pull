from typing import Optional

from ..config import get_config
from ..envelope import envelope
from ..sources import logistics


def shipping_quote(origin: str = "CN", destination: str = "US", mode: str = "sea",
                   weight_kg: float = 100.0, locale: Optional[str] = None) -> dict:
    """Shipping quote: sea / air / express.

    Live quotes need an enterprise logistics API key (SF Express Intl /
    4PX / Yanwen); public fallback returns guidance, not a fabricated price.
    `locale` (or `destination` country) switches buyer-facing copy; default EN.
    """
    cfg = get_config()
    res = logistics.shipping_quote(cfg, origin, destination, mode, weight_kg)
    quality = "live" if res.get("available") else "degraded"
    return envelope(res, source=res.get("via", "none"), data_quality=quality,
                    locale=locale, locale_key="shipping", destination=destination)
