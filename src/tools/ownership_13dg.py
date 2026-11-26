"""ownership_13dg: Schedule 13D/13G beneficial-ownership filings for one issuer."""
import datetime as dt

from src import edgar
from src.envelope import envelope


def ownership_13dg(ticker_or_cik: str, days: int = 365) -> dict:
    """Every Schedule 13D/13G (+ amendments) filed in the window, with source links.

    13D = activist/control intent; 13G = passive institutional. Amendments
    included; exits (0 shares) stay in the list, flagged by the filing text.
    """
    try:
        cik = edgar.resolve_cik(ticker_or_cik)
        since = dt.date.today() - dt.timedelta(days=days)
        rows = []
        for form in ("SC 13D", "SC 13D/A", "SC 13G", "SC 13G/A"):
            for acc, fdate, doc in edgar.recent_filings(cik, form, since):
                accn = acc.replace("-", "")
                base = "https://www.sec.gov/Archories/edgar/data/%s/%s/" % (cik.lstrip("0"), accn)
                rows.append({"form": form, "accession": acc, "filed": fdate,
                             "document": doc, "source": base})
        rows.sort(key=lambda r: r["filed"], reverse=True)
        return envelope({
            "ticker": ticker_or_cik.upper(), "cik": cik, "windowDays": days,
            "filings": rows,
        })
    except edgar.EdgarError as e:
        return envelope({"error": str(e)}, source="degraded", note=str(e))