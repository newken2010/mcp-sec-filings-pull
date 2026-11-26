"""FastMCP entrypoint: registers all 7 China-sourcing tools.

Run:  python main.py            (stdio MCP server)
Test: pytest tests/ -q          (offline, mocks data sources)

Compliance-first: no supplier details persisted; public sources on,
enterprise 1688/国际站 API off by default (needs 企业资质).

Buyer-facing copy is EN by default; every tool accepts `locale` to switch
(de/fr/es/ja/ko). For tariff/shipping, `destination` country also auto-selects.
"""
from fastmcp import FastMCP

from src.config import get_config
from src.tools.find_factory import find_factory as _find_factory
from src.tools.price_compare import price_compare as _price_compare
from src.tools.moq_check import moq_check as _moq_check
from src.tools.supplier_verify import supplier_verify as _supplier_verify
from src.tools.shipping_quote import shipping_quote as _shipping_quote
from src.tools.duty_calc import duty_calc as _duty_calc
from src.tools.trend_hot import trend_hot as _trend_hot

mcp = FastMCP("china-sourcing-map")


@mcp.tool()
def find_factory(category: str, region: str | None = None, limit: int = 10,
                 locale: str | None = None) -> dict:
    """Find factories/suppliers for a category in a CN region (public fields only).

    category: e.g. "stainless steel bottle". region: e.g. "Yiwu", "Guangdong".
    locale: buyer-facing copy language (default en; de/fr/es/ja/ko).
    """
    return _find_factory(category, region, limit, locale)


@mcp.tool()
def price_compare(category: str, limit: int = 10, locale: str | None = None) -> dict:
    """Compare prices across suppliers for the same category.

    locale: buyer-facing copy language (default en; de/fr/es/ja/ko).
    """
    return _price_compare(category, limit, locale)


@mcp.tool()
def moq_check(offer_id: str, locale: str | None = None) -> dict:
    """MOQ / lead time / freight for a public 1688/Alibaba.com offer.

    offer_id: public listing id or URL. locale: default en; de/fr/es/ja/ko.
    """
    return _moq_check(offer_id, locale)


@mcp.tool()
def supplier_verify(company: str, region: str | None = None,
                    locale: str | None = None) -> dict:
    """Verify a supplier via public credit + customs + trade-feedback signals.

    Read-only, no private data stored. locale: default en; de/fr/es/ja/ko.
    """
    return _supplier_verify(company, region, locale)


@mcp.tool()
def shipping_quote(origin: str = "CN", destination: str = "US", mode: str = "sea",
                   weight_kg: float = 100.0, locale: str | None = None) -> dict:
    """Shipping quote: sea/air/express (live quote needs a logistics API key).

    `destination` country auto-selects buyer copy language if `locale` is omitted.
    """
    return _shipping_quote(origin, destination, mode, weight_kg, locale)


@mcp.tool()
def duty_calc(hs_code: str, origin: str = "CN", destination: str = "US",
              locale: str | None = None) -> dict:
    """Estimate duty/tariff for an HS code (live for US via USITC HTS).

    Planning only. `destination` country auto-selects copy language if `locale` omitted.
    """
    return _duty_calc(hs_code, origin, destination, locale)


@mcp.tool()
def trend_hot(category: str | None = None, limit: int = 10,
              locale: str | None = None) -> dict:
    """Overseas hot-selling category trend signal (public).

    locale: buyer-facing copy language (default en; de/fr/es/ja/ko).
    """
    return _trend_hot(category, limit, locale)


if __name__ == "__main__":
    # confirm the config shape at startup so misconfig fails loud
    _ = get_config()
    mcp.run()
