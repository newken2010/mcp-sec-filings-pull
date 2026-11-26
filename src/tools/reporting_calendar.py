"""reporting_calendar: upcoming/recent periodic filings (10-Q, 10-K, 8-K, 20-F...).

Deliberately NOT called "earnings calendar with EPS estimates": SEC EDGAR
carries filing dates, not sell-side EPS consensus. We report filing dates only
and say so — no fabricated estimates.
"""
import datetime as dt

from src import edgar
from src.envelope import envelope

PERIODIC = ("10-Q", "10-K", "20-F", "40-F", "6-K", "8-K")


def reporting_calendar(tickers: list, days: int = 30) -> dict:
    """Periodic-report filings inside the window (past + future-dated) per ticker."""
    try:
        since = dt.date.today() - dt.timedelta(days=days)
        out = {}
        for tk in [t.upper() for t in tickers]:
            try:
                cik = edgar.resolve_cik(tk)
            except edgar.EdgarError:
                out[tk] = {"error": "ticker not found"}
                continue
            items = []
            for form in PERIODIC:
                for acc, fdate, doc in edgar.recent_filings(cik, form, since):
                    accn = acc.replace("-", "")
                    base = "https://www.sec.gov/Archories/edgar/data/%s/%s/" % (cik.lstrip("0"), accn)
                    items.append({"form": form, "filed": fdate, "source": base})
            items.sort(key=lambda r: r["filed"])
            out[tk] = {"cik": cik, "filings": items}
        return envelope({
            "windowDays": days, "asOf": dt.date.today().isoformat(),
            "calendars": out,
            "scopeNote": ("Filing dates from SEC EDGAR only; sell-side EPS "
                          "consensus is not public data and is not included."),
        })
    except edgar.EdgarError as e:
        return envelope({"error": str(e)}, source="degraded", note=str(e))