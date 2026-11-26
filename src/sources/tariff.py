"""US tariff lines (USITC HTS, free/public) + public FX rates.

USITC HTS REST API: https://hts.usitc.gov/reststop/search — free, no key,
returns the US tariff schedule line with general / special / other rates.

FX: ECB reference rates via frankfurter.app — free, no key, updated daily.

Only US tariff lines have a free public API. Other destinations return a
degraded marker (use a licensed broker / paid tariff provider) — we never
guess a duty rate.
"""
from __future__ import annotations
import re
import requests
from typing import Optional

from ..config import SourceConfig

USITC_SEARCH = "https://hts.usitc.gov/reststop/search"
FX_BASE = "https://api.frankfurter.app/latest"


def _parse_rate(text: Optional[str]) -> Optional[float]:
    """'Free' -> 0.0, '35%' -> 35.0, '2.5%' -> 2.5; unparsable -> None."""
    if not isinstance(text, str):
        return None
    t = text.strip().lower()
    if t.startswith("free"):
        return 0.0
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", t)
    return float(m.group(1)) if m else None


def _clean(hs_code: str) -> str:
    return hs_code.replace(" ", "").strip()


def get_tariff_line(cfg: SourceConfig, hs_code: str, origin: str = "CN",
                    destination: str = "US") -> dict:
    """Return the tariff line + duty rate for an HS code, origin -> destination.

    Live for US destinations (USITC HTS). Degrades with a marker when the
    endpoint is unreachable, the HS code has no match, or the destination is
    not covered by a free public API.
    """
    if not cfg.tariff_public or not hs_code:
        return {"available": False, "dataQuality": "degraded", "via": "tariff",
                "note": "Tariff source disabled or HS code missing."}

    dest = (destination or "").strip().upper()
    if dest != "US":
        return {
            "available": False,
            "dataQuality": "degraded",
            "via": "tariff",
            "hs_code": hs_code,
            "destination": dest,
            "note": (f"No free public tariff API for {dest or 'this destination'}. "
                     "Only US lines are available (USITC HTS); use a licensed "
                     "customs broker or a paid tariff data provider for other markets."),
        }

    prefix = _clean(hs_code)
    try:
        r = requests.get(USITC_SEARCH, params={"keyword": prefix}, timeout=10,
                         headers={"User-Agent": cfg.user_agent})
        r.raise_for_status()
        rows = r.json()
    except (requests.RequestException, ValueError):
        return {"available": False, "dataQuality": "degraded", "via": "usitc_hts",
                "hs_code": hs_code, "destination": dest,
                "note": "USITC HTS endpoint unreachable; rate not returned."}

    if not isinstance(rows, list) or not rows:
        return {"available": False, "dataQuality": "degraded", "via": "usitc_hts",
                "hs_code": hs_code, "destination": dest,
                "note": f"No HTS line matched '{hs_code}'."}

    row = next((x for x in rows
                if str(x.get("htsno", "")).startswith(prefix)), rows[0])
    general = row.get("general")
    return {
        "available": True,
        "dataQuality": "live",
        "via": "usitc_hts",
        "hs_code": hs_code,
        "hts_code": row.get("htsno"),
        "description": row.get("description"),
        "destination": dest,
        "duty_rate_text": general,
        "duty_rate_percent": _parse_rate(general),
        "special_rate_text": row.get("special"),
        "other_rate_text": row.get("other"),
        "units": row.get("units", []),
    }


def get_fx_rate(cfg: SourceConfig, base: str = "USD", target: str = "CNY") -> Optional[float]:
    """Public FX rate base -> target; None when unavailable."""
    if not cfg.fx_public:
        return None
    try:
        r = requests.get(FX_BASE, params={"from": base, "to": target}, timeout=8,
                         headers={"User-Agent": cfg.user_agent})
        r.raise_for_status()
        return float(r.json().get("rates", {}).get(target))
    except (requests.RequestException, ValueError, TypeError, AttributeError):
        return None
