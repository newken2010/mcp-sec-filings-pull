---
name: mcp-sec-filings-pull
description: SEC EDGAR public filings pull — insider sales (Form 4), insider-cluster ranking, new insiders (Form 3), 13D/13G ownership, reporting calendar. Use when asked about insider selling, beneficial ownership, filing dates, or US public-company filings data.
---

# mcp-sec-filings-pull

Read-only SEC EDGAR public-API toolset. Every deliverable row carries its live
EDGAR source URL; nothing is fabricated; empty results are reported as empty.

## Tools

- `insider_sales(ticker_or_cik, days=30, limit=200)` — Form 4 code S rows for
  one issuer: owner, date, shares, price, EDGAR source. Ranked by value.
- `insider_clusters(tickers=None, days=30, min_sellers=3)` — scan a watchlist
  (default 15 large caps), rank issuers by distinct sellers in the window.
- `new_insiders(tickers, days=30)` — Form 3 filings (opening stakes).
- `ownership_13dg(ticker_or_cik, days=365)` — 13D/13G + amendments.
- `reporting_calendar(tickers, days=30)` — 10-Q/10-K/8-K/20-F filing dates.
  Filing dates only — no EPS consensus (not public data).

## Response envelope

`data` / `source` ("sec_edgar" | "degraded") / `dataQuality` / `disclaimer`
/ `asOf`. On lookup failure the tool degrades with an `error` note instead of
raising.

## Example

```
insider_sales("AAPL", days=30)
→ data.sales: [{owner, txnDate, shares, price, source: "https://www.sec.gov/Archives/..."}]
```

## Tests

`pytest tests/ -q` — offline; parses a real-shaped Form 4 XML and checks the
code-S filter, cluster ranking, and empty-result honesty.