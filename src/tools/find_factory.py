from typing import Optional

from ..config import get_config
from ..envelope import envelope
from ..sources import public_web


def find_factory(category: str, region: Optional[str] = None, limit: int = 10,
                 locale: Optional[str] = None) -> dict:
    """Find factories/suppliers for a category in a CN region.

    Public display fields only; no supplier details persisted. With
    1688/国际站 enterprise API enabled this returns authoritative listings.
    `locale` switches buyer-facing copy (default EN; de/fr/es/ja/ko supported).
    """
    cfg = get_config()
    hits = public_web.find_supplier_hits(cfg, category, region, limit=limit)
    # no enterprise API / no public hits -> degraded, never "public" with zero data
    quality = "live" if hits.get("available") else "degraded"
    return envelope(hits, source=hits.get("via", "none"), data_quality=quality,
                    locale=locale, locale_key="supplier")
