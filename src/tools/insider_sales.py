"""insider_sales: Form 4 open-market sales (code S) for one issuer."""
import datetime as dt

from src import edgar
from src.envelope import envelope


def insider_sales(ticker_or_cik: str, days: int = 30, limit: int = 200) -> dict:
    """Open-market insider sales (transaction code S) from SEC Form 4 filings.

    ticker_or_cik: e.g. "AAPL" or "0000320193". days: look-back window.
    Every row carries the live EDGAR filing source URL.
    """
    try:
        cik = edgar.resolve_cik(ticker_or_cik)
        since = dt.date.today() - dt.timedelta(days=days)
        filings = edgar.recent_filings(cik, "4", since)
        rows = []
        for acc, fdate, doc in filings:
            try:
                issuer, txns, base = edgar.form4_transactions_doc(cik, acc, doc)
            except edgar.EdgarError:
                continue
            for owner, date, code, sh, pr in txns:
                if code != "S":
                    continue
                rows.append({
                    "ticker": ticker_or_cik.upper(), "issuer": issuer, "owner": owner,
                    "txnDate": date, "filed": fdate, "shares": sh,
                    "price": pr, "source": base,
                })
        rows.sort(key=lambda r: -(r["shares"] * (r["price"] or 0)))
        return envelope({
            "ticker": ticker_or_cik.upper(), "cik": cik, "windowDays": days,
            "form4Filings": len(filings), "sales": rows[:limit],
        })
    except edgar.EdgarError as e:
        return envelope({"error": str(e)}, source="degraded", note=str(e))