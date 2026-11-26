from typing import Optional

from ..config import get_config
from ..envelope import envelope
from ..sources import public_web


def price_compare(category: str, limit: int = 10, locale: Optional[str] = None) -> dict:
    """Compare prices across suppliers for the same category.

    `locale` switches buyer-facing copy (default EN; de/fr/es/ja/ko supported).
    """
    cfg = get_config()
    snap = public_web.price_snapshot(cfg, category)
    quality = "live" if snap.get("available") else "degraded"
    return envelope(snap, source=snap.get("via", "none"), data_quality=quality,
                    locale=locale, locale_key="supplier")
