"""SEC EDGAR public-API client (read-only, free, no credentials).

Endpoints used:
  - https://www.sec.gov/files/company_tickers.json        ticker -> CIK map
  - https://data.sec.gov/submissions/CIK##########.json    filing history
  - https://www.sec.gov/Archives/edgar/data/.../form4.xml Form 4 structured XML

Etiquette: SEC asks for a descriptive User-Agent and <=10 req/s. We default
to ~8 req/s with a polite UA and cache the ticker map on disk (it changes
rarely). No data is persisted beyond the request except that cache.
"""
import datetime as dt
import json
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

UA = "mcp-sec-filings-pull/0.1 (research; contact: agent@example.com)"
CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"
_MIN_INTERVAL = 0.12  # seconds between requests


class EdgarError(RuntimeError):
    pass


_last_call = 0.0


def _throttle():
    global _last_call
    wait = _MIN_INTERVAL - (time.monotonic() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.monotonic()


def get_json(url: str, retries: int = 3) -> dict:
    for i in range(retries):
        _throttle()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i == retries - 1:
                raise EdgarError("GET %s failed: %r" % (url, e))
            time.sleep(1.5 * (i + 1))
    raise EdgarError("unreachable")


def get_bytes(url: str, retries: int = 3) -> bytes:
    for i in range(retries):
        _throttle()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:
            if i == retries - 1:
                raise EdgarError("GET %s failed: %r" % (url, e))
            time.sleep(1.5 * (i + 1))
    raise EdgarError("unreachable")


def ticker_to_cik_map() -> dict:
    """ticker (upper) -> zero-padded 10-digit CIK. Cached on disk."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = CACHE_DIR / "company_tickers.json"
    if not cache.exists():
        cache.write_bytes(get_bytes("https://www.sec.gov/files/company_tickers.json"))
    raw = json.loads(cache.read_text(encoding="utf-8"))
    return {v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in raw.values()}


def resolve_cik(ticker_or_cik: str) -> str:
    s = (ticker_or_cik or "").strip()
    if s.upper().startswith("CIK") or s.isdigit():
        return s.upper().replace("CIK", "").strip().zfill(10)
    m = ticker_to_cik_map()
    cik = m.get(s.upper())
    if not cik:
        raise EdgarError("ticker %r not found in SEC company_tickers.json" % s)
    return cik


def submissions(cik: str) -> dict:
    return get_json("https://data.sec.gov/submissions/CIK%s.json" % cik)


def recent_filings(cik: str, form: str, since: dt.date) -> list:
    """[(accession, filingDate, primaryDocument)] for `form` filed on/after since."""
    sub = submissions(cik)
    r = sub.get("filings", {}).get("recent", {})
    out = []
    for f, a, d, doc in zip(r.get("form", []), r.get("accessionNumber", []),
                            r.get("filingDate", []), r.get("primaryDocument", [])):
        if f == form and d >= since.isoformat():
            out.append((a, d, doc))
    return out


def archives_base(cik: str, accession: str) -> str:
    """EDGAR Archives directory URL for a filing.

    Empirical rules (verified 2026-11-27): the raw structured XML sits at the
    directory ROOT with a varying filename (form4.xml, ownership.xml,
    form4-<date>_<time>.xml), while `xslF345X06/<same name>` is the XSL HTML
    view — never parse that as XML. The directory may resolve under the
    ISSUER CIK or the FILER CIK (accession prefix) depending on the filing,
    and SEC answers a missing directory with HTTP 200 + soft-404 HTML, so
    callers must inspect payloads, not status codes.
    """
    return "https://www.sec.gov/Archives/edgar/data/%s/%s/" % (
        cik.lstrip("0"), accession.replace("-", ""))


def _index_raw_xml(base: str, accession: str) -> str:
    """Raw Form 4 XML URL from the filing's index page (authoritative doc list).

    The index page (`<accession>-index.htm`) lists every document; we take
    the .xml link that is NOT the xslF345X06 HTML view. Returns "" when the
    index page is missing or lists no raw XML.
    """
    import re as _re
    try:
        html = get_bytes(base + accession + "-index.htm").decode("utf-8", "replace")
    except EdgarError:
        return ""
    for href in _re.findall(r'href="([^"]+)"', html):
        if not href.endswith(".xml") or "xslF345X06" in href:
            continue
        if href.startswith("http"):
            return href
        if href.startswith("/"):
            return "https://www.sec.gov" + href
        return base + href
    return ""


def _form4_from_base(base: str, accession: str) -> tuple:
    """Fetch + parse the raw Form 4 XML for one candidate directory."""
    for name in ("form4.xml",):
        try:
            xml_bytes = get_bytes(base + name)
        except EdgarError:
            continue
        if b"<ownershipDocument" in xml_bytes[:2000]:
            return _parse_form4(xml_bytes, base)
    link = _index_raw_xml(base, accession)
    if link:
        try:
            xml_bytes = get_bytes(link)
        except EdgarError:
            xml_bytes = None
        if xml_bytes and b"<ownershipDocument" in xml_bytes[:2000]:
            return _parse_form4(xml_bytes, link.rsplit("/", 1)[0] + "/")
    raise EdgarError("no raw Form 4 XML under %s" % base)


def form4_transactions(cik: str, accession: str) -> tuple:
    """Parse a Form 4 filing -> (issuer, [(owner, date, code, shares, price)])."""
    base = archives_base(cik, accession)
    try:
        return _form4_from_base(base, accession)
    except EdgarError:
        filer_base = archives_base(accession.split("-")[0], accession)
        if filer_base != base:
            return _form4_from_base(filer_base, accession)
        raise


def form4_transactions_doc(cik: str, accession: str, primary_doc: str) -> tuple:
    """Form 4 transactions. `primary_doc` is accepted for call compatibility;
    the raw XML is located via the conventional root name, then the filing
    index page, then the filer-CIK directory. HTML views are never parsed."""
    return form4_transactions(cik, accession)


def _parse_form4(xml_bytes: bytes, source_base: str) -> tuple:
    root = ET.fromstring(xml_bytes)
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"

    def text(el, path, default=""):
        e = el.find(ns + path)
        return (e.text or "").strip() if e is not None else default

    issuer = text(root, "issuer/issuerName")
    owner = text(root, "reportingOwner/reportingOwnerId/rptOwnerName") or \
        text(root, "reportingOwner/reportingOwnerId/rptOwnerCik")
    rows = []
    for t in list(root.iter(ns + "nonDerivativeTransaction")) + \
            list(root.iter(ns + "derivativeTransaction")):
        code = text(t, "transactionCoding/transactionCode")
        amounts = t.find(ns + "transactionAmounts")
        if amounts is None:
            continue
        shares = text(amounts, "transactionShares/value")
        pps = text(amounts, "transactionPricePerShare/value")
        date = text(t, "transactionDate/value")
        if not (date and code and shares):
            continue
        try:
            sh = float(shares)
            pr = float(pps) if pps else None
        except ValueError:
            continue
        rows.append((owner, date, code, sh, pr))
    return issuer, rows, source_base