"""new_insiders: Form 3 initial-ownership filings (someone just became insider)."""
import datetime as dt

from src import edgar
from src.envelope import envelope


def new_insiders(tickers: list, days: int = 30) -> dict:
    """Form 3 filings = the moment a person becomes an insider (opening stake).

    Note: Form 3 XML does not carry a uniform machine-readable share field
    across all filers; rows below carry filing metadata + source link, and
    `parsedShares` only when the XML exposed it cleanly.
    """
    try:
        since = dt.date.today() - dt.timedelta(days=days)
        rows, n = [], 0
        for tk in [t.upper() for t in tickers]:
            try:
                cik = edgar.resolve_cik(tk)
                filings = edgar.recent_filings(cik, "3", since)
            except edgar.EdgarError:
                continue
            n += len(filings)
            for acc, fdate, doc in filings:
                base = edgar.archives_base(cik, acc)
                rows.append({"ticker": tk, "accession": acc, "filed": fdate,
                             "document": doc, "source": base})
        return envelope({"windowDays": days, "form3Filings": n, "filings": rows})
    except edgar.EdgarError as e:
        return envelope({"error": str(e)}, source="degraded", note=str(e))