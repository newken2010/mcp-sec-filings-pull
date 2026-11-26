"""Data-source feature flags.

Compliance-first design: public/read-only sources are ON by default so the
server works with zero enterprise credentials. The 1688 open-platform
enhancement layer is OFF by default (requires 企业资质) — plug it in when
available, never block on it.

All adapters return the same shape; when a source is disabled or its live
endpoint is unreachable, the tool degrades to public data + a `dataQuality`
marker instead of failing. No supplier details are cached beyond the request.
"""
from dataclasses import dataclass


@dataclass
class SourceConfig:
    public_web: bool = True      # 1688 / 国际站 public display fields, read-only, not persisted
    tariff_public: bool = True   # USITC HTS tariff lines (free, public)
    fx_public: bool = True       # public FX rate endpoints
    logistics_public: bool = True  # carrier public rates where available
    alibaba_1688_api: bool = False  # enterprise 1688 open-platform API (needs 企业资质)
    alibaba_intl_api: bool = False   # 阿里国际站 open API (needs 企业资质)
    biggo: bool = False           # BigGo-MCP cross-platform price (MIT, optional)
    user_agent: str = "mcp-china-sourcing-map/0.1"


def get_config() -> SourceConfig:
    return SourceConfig()
