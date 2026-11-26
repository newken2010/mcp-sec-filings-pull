"""Public web adapters: read-only, display fields only, nothing persisted.

Design rules (compliance-first):
- Only publicly displayed info is read (product name, public price range,
  MOQ shown on listing, region). No off-platform scraping of private data.
- Results are returned in-request; no local supplier cache is written.
- 1688/国际站 official API slots live in `alibaba_1688_api` /
  `alibaba_intl_api` config flags; when enabled they replace public data
  with authoritative API responses.
"""
from typing import Optional
from urllib.parse import urlparse

from ..config import SourceConfig

_SEARCH_HOSTS = ("1688.com", "alibaba.com")


def _host_allowed(url: str, hosts=_SEARCH_HOSTS) -> bool:
    """True only when the URL's host (not a query/fragment substring) is one of
    the known public search hosts. Scheme-pinned, so an attacker cannot reach a
    host via a `?x=1688.com` / `#1688.com` parameter."""
    host = (urlparse(url).hostname or "").lower()
    return any(host == h or host.endswith("." + h) for h in hosts)


def find_supplier_hits(cfg: SourceConfig, category: str, region: Optional[str],
                       limit: int = 10) -> dict:
    """Return candidate supplier listings for a category/region.

    With enterprise API flags enabled this would call 1688/国际站 open APIs,
    capped at `limit` rows. The public fallback returns a structured "no live
    data" marker (still carrying the `limit`) so the tool layer degrades
    gracefully and answers with guidance instead of invented suppliers.
    """
    limit = max(0, int(limit or 0))
    if cfg.alibaba_1688_api:
        # TODO: 1688 open-platform 商品搜索/供应商筛选 (needs 企业资质)
        return {"available": True, "via": "1688_open_api", "items": [], "limit": limit}
    if cfg.alibaba_intl_api:
        # TODO: 阿里国际站 cross-border product API
        return {"available": True, "via": "alibaba_intl_api", "items": [], "limit": limit}
    return {
        "available": False,
        "via": "public_web",
        "items": [],
        "limit": limit,
        "note": (
            "No enterprise API credentials configured. Public search of "
            f"'{category}' in {region or 'CN'} requires 1688/国际站 public pages; "
            "enable a source or provide credentials."
        ),
    }


def moq_public_fields(cfg: SourceConfig, offer_id: str) -> dict:
    """MOQ / lead time / freight as publicly displayed on the listing.

    No listing adapter is configured yet, so every field is None and the
    payload is marked as having no data — the tool layer reports degraded.
    """
    return {
        "available": False,
        "via": "public_web",
        "offer_id": offer_id,
        "moq": None,
        "lead_time_days": None,
        "freight_note": "public display fields only",
        "note": ("No listing adapter configured: open the offer on 1688 / "
                 "Alibaba.com to read MOQ, lead time and freight, or enable "
                 "the enterprise API."),
    }


def price_snapshot(cfg: SourceConfig, category: str) -> dict:
    """Cross-supplier price compare from public listings.

    BigGo-MCP (MIT) can be wired in via `cfg.biggo` for 淘宝/速卖通/阿里系.
    """
    if cfg.biggo:
        # TODO: BigGo-MCP-Server cross-platform price + history (MIT)
        return {"available": True, "via": "biggo", "items": []}
    return {
        "available": False,
        "via": "public_web",
        "items": [],
        "note": "Public price compare needs 国际站/1688 public listings or BigGo.",
    }


def verify_url(url: str) -> bool:
    return _host_allowed(url)
