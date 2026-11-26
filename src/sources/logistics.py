"""Logistics quote + hot-trend placeholders.

Real carriers (顺丰国际/递四方/燕文) need enterprise API keys; public
fallback returns a structured marker so the tool degrades cleanly.
Trend hot uses 阿里国际站 public trend pages when reachable.
"""
from typing import Optional

from ..config import SourceConfig


def shipping_quote(cfg: SourceConfig, origin: str, destination: str, mode: str, weight_kg: float) -> dict:
    """Sea/air/express quote. mode in {sea, air, express}."""
    if cfg.logistics_public:
        return {
            "available": False,
            "via": "public",
            "note": (
                f"Public carrier rates for {origin}->{destination} ({mode}, "
                f"{weight_kg}kg) need a logistics API key (顺丰国际/递四方/燕文). "
                "Configure an enterprise key to get live quotes."
            ),
        }
    return {"available": False, "note": "Logistics source disabled."}


def trend_hot(cfg: SourceConfig, category: Optional[str] = None, limit: int = 10) -> dict:
    """Overseas hot-selling category trend (阿里国际站 public trend pages)."""
    return {
        "available": False,
        "via": "public_web",
        "items": [],
        "note": "Trend data needs 阿里国际站 public trend endpoint; wire a source.",
    }
