# mcp-sec-filings-pull

[![mcp-sec-filings-pull MCP server](https://glama.ai/mcp/servers/newken2010/mcp-sec-filings-pull/badges/score.svg)](https://glama.ai/mcp/servers/newken2010/mcp-sec-filings-pull)

MCP toolset for **SEC EDGAR public filings** — insider trading, beneficial
ownership, and reporting calendars. Read-only, public API only: no credentials,
no paid data vendors, nothing fabricated. Every row carries its live EDGAR
source URL.

## Tools

| Tool | What it returns |
|---|---|
| `insider_sales(ticker_or_cik, days=30)` | Form 4 open-market sales (code S) for one issuer, ranked by value |
| `insider_clusters(tickers=None, days=30, min_sellers=3)` | Issuers where N+ distinct insiders sold in the window, ranked |
| `new_insiders(tickers, days=30)` | Form 3 filings — who just became an insider (opening stake) |
| `ownership_13dg(ticker_or_cik, days=365)` | Schedule 13D/13G (+amendments) with source links |
| `reporting_calendar(tickers, days=30)` | Periodic filing dates (10-Q/10-K/8-K/20-F...) |

## Honest scope

- `reporting_calendar` returns **filing dates only**. Sell-side EPS consensus
  is not public data and is deliberately not included — no invented estimates.
- Empty results are reported as empty with a note, never padded.
- Figures come from the filings themselves; not investment advice.

## Run

```
python main.py        # stdio MCP server
pytest tests/ -q      # offline tests (mocked endpoints, real XML shapes)
```

## Data source

- `https://www.sec.gov/files/company_tickers.json` — ticker→CIK map (cached on disk)
- `https://data.sec.gov/submissions/CIK##########.json` — filing history
- `https://www.sec.gov/Archives/edgar/data/.../<accession>-index.htm` — filing
  document list; the raw Form 4 XML sits at the directory root but its filename
  varies (`form4.xml`, `ownership.xml`, `form4-<date>_<time>.xml`), and the
  directory may resolve under the issuer CIK or the filing-agent CIK. The
  client tries the conventional root name first, then reads the index page for
  the authoritative raw-XML link (the `xslF345X06/` copy is the XSL HTML view
  and is never parsed as XML). SEC answers missing directories with HTTP 200 +
  a soft-404 HTML page, so payloads are checked, not status codes.

Etiquette: descriptive User-Agent, ≤10 req/s, ticker map cached.

## License

MIT.