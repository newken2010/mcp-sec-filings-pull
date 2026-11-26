"""Shared response envelope + data-quality markers.

Every tool returns:
  data:        payload (list or dict)
  source:      "sec_edgar" | "degraded"
  dataQuality: "live" | "degraded"
  disclaimer:  always present — filings-only, not investment advice
  asOf:        ISO timestamp of the pull
"""
import datetime as dt


def envelope(data, source="sec_edgar", as_of=None, note=None):
    return {
        "data": data,
        "source": source,
        "dataQuality": "live" if source == "sec_edgar" else "degraded",
        "disclaimer": ("Figures come from SEC EDGAR filings themselves; "
                       "not investment advice or forecasts."),
        "asOf": as_of or dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "note": note,
    }