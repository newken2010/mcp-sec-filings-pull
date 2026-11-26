"""insider_clusters: issuers where 3+ distinct insiders sold in the window."""
import datetime as dt

from src import edgar
from src.envelope import envelope

DEFAULT_WATCHLIST = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META",
                     "AVGO", "AMD", "NFLX", "CRM", "ORCL", "ADBE", "QCOM", "INTC"]


def insider_clusters(tickers: list | None = None, days: int = 30,
                     min_sellers: int = 3) -> dict:
    """Rank issuers by distinct insider sellers (Form 4 code S) in the window.

    tickers: watchlist to scan (default: 15 large caps). min_sellers: cluster
    threshold. Returns ranked clusters + the strongest single sale per issuer.
    """
    tickers = [t.upper() for t in (tickers or DEFAULT_WATCHLIST)]
    since = dt.date.today() - dt.timedelta(days=days)
    per_ticker, n_filings = {}, 0
    for tk in tickers:
        try:
            cik = edgar.resolve_cik(tk)
            filings = edgar.recent_filings(cik, "4", since)
        except edgar.EdgarError:
            per_ticker[tk] = {"error": "resolve/list failed"}
            continue
        n_filings += len(filings)
        sales = []
        for acc, fdate, doc in filings:
            try:
                issuer, txns, base = edgar.form4_transactions_doc(cik, acc, doc)
            except edgar.EdgarError:
                continue
            for owner, date, code, sh, pr in txns:
                if code == "S":
                    sales.append({"owner": owner, "txnDate": date, "filed": fdate,
                                  "shares": sh, "price": pr, "source": base})
        per_ticker[tk] = {"form4Filings": len(filings), "sales": sales}
    clusters = []
    for tk, blob in per_ticker.items():
        sales = blob.get("sales") or []
        sellers = {s["owner"] for s in sales}
        if len(sellers) >= min_sellers:
            top = max(sales, key=lambda s: s["shares"] * (s["price"] or 0), default=None)
            clusters.append({
                "ticker": tk, "distinctSellers": len(sellers),
                "totalShares": sum(s["shares"] for s in sales),
                "saleCount": len(sales),
                "strongestSingleSale": top,
            })
    clusters.sort(key=lambda c: (-c["distinctSellers"], -c["totalShares"]))
    return envelope({
        "windowDays": days, "minSellers": min_sellers,
        "scannedTickers": tickers, "form4FilingsTotal": n_filings,
        "clusters": clusters,
        "emptyResultNote": ("No issuer reached the threshold in this window — "
                            "reported as-is, not padded.") if not clusters else None,
    })