from typing import Optional

from ..config import get_config
from ..envelope import envelope
from ..sources import logistics


def trend_hot(category: Optional[str] = None, limit: int = 10,
              locale: Optional[str] = None) -> dict:
    """Overseas hot-selling category trend.

    Reads Alibaba.com public trend pages when a source is wired; public
    fallback returns guidance rather than invented rankings.
    `locale` switches buyer-facing copy (default EN; de/fr/es/ja/ko supported).
    """
    cfg = get_config()
    res = logistics.trend_hot(cfg, category, limit)
    quality = "live" if res.get("available") else "degraded"
    return envelope(res, source=res.get("via", "none"), data_quality=quality,
                    locale=locale, locale_key="trend")
