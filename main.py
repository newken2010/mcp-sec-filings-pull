"""FastMCP entrypoint: SEC EDGAR public-filings pull toolset.

Run:  python main.py            (stdio MCP server)
Test: pytest tests/ -q          (offline, mocks SEC endpoints)

Data policy: read-only SEC EDGAR public API only — no credentials, no paid
vendors, nothing fabricated. Every row carries its live EDGAR source URL.
"""
from fastmcp import FastMCP

from src.tools.insider_sales import insider_sales as _insider_sales
from src.tools.insider_clusters import insider_clusters as _insider_clusters
from src.tools.new_insiders import new_insiders as _new_insiders
from src.tools.ownership_13dg import ownership_13dg as _ownership_13dg
from src.tools.reporting_calendar import reporting_calendar as _reporting_calendar

mcp = FastMCP("sec-filings-pull")


@mcp.tool()
def insider_sales(ticker_or_cik: str, days: int = 30, limit: int = 200) -> dict:
    """Open-market insider sales (Form 4 code S) for one issuer, with EDGAR source links.

    ticker_or_cik: "AAPL" or "0000320193". days: look-back window (default 30).
    """
    return _insider_sales(ticker_or_cik, days, limit)


@mcp.tool()
def insider_clusters(tickers: list | None = None, days: int = 30,
                     min_sellers: int = 3) -> dict:
    """Rank issuers by distinct insider sellers in the window (Form 4 code S).

    tickers: watchlist to scan (default: 15 large caps). min_sellers: cluster
    threshold (default 3). Empty results are reported as-is, never padded.
    """
    return _insider_clusters(tickers, days, min_sellers)


@mcp.tool()
def new_insiders(tickers: list, days: int = 30) -> dict:
    """Form 3 initial-ownership filings — who just became an insider (opening stake)."""
    return _new_insiders(tickers, days)


@mcp.tool()
def ownership_13dg(ticker_or_cik: str, days: int = 365) -> dict:
    """Schedule 13D/13G (+amendments) beneficial-ownership filings with source links."""
    return _ownership_13dg(ticker_or_cik, days)


@mcp.tool()
def reporting_calendar(tickers: list, days: int = 30) -> dict:
    """Periodic-report filing dates (10-Q/10-K/8-K...) from SEC EDGAR.

    Filing dates only — sell-side EPS consensus is not public data and is not included.
    """
    return _reporting_calendar(tickers, days)


def main():
    mcp.run()


if __name__ == "__main__":
    main()