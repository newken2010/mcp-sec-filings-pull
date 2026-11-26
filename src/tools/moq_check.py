from typing import Optional

from ..config import get_config
from ..envelope import envelope
from ..sources import public_web


def moq_check(offer_id: str, locale: Optional[str] = None) -> dict:
    """MOQ / lead time / freight for a public 1688 / Alibaba.com offer.

    offer_id: public listing id or URL. Only publicly displayed fields are read.
    `locale` switches buyer-facing copy (default EN; de/fr/es/ja/ko supported).
    """
    cfg = get_config()
    fields = public_web.moq_public_fields(cfg, offer_id)
    quality = "public" if fields.get("available") else "degraded"
    return envelope(fields, source=fields.get("via", "public_web"), data_quality=quality,
                    locale=locale, locale_key="supplier")
