from typing import Optional

from ..config import get_config
from ..envelope import envelope
from ..sources import tariff


def duty_calc(hs_code: str, origin: str = "CN", destination: str = "US",
              locale: Optional[str] = None) -> dict:
    """Estimate duty/tariff for an HS code, origin->destination.

    Live for US destinations via the free USITC HTS API; other destinations
    degrade to guidance (no free public tariff API). Planning only — confirm
    with a licensed broker.
    `locale` (or `destination` country) switches buyer-facing copy; default EN.
    """
    cfg = get_config()
    res = tariff.get_tariff_line(cfg, hs_code, origin, destination)
    return envelope(res, source=res.get("via", "degraded"),
                    data_quality=res.get("dataQuality", "degraded"),
                    locale=locale, locale_key="tariff", destination=destination)
