# -*- coding: utf-8 -*-
"""Offline tests: parse a real-shaped Form 4 XML and check tool logic.
No network: edgar client functions are monkeypatched where needed."""
import datetime as dt
import xml.etree.ElementTree as ET

import pytest

from src import edgar
from src.tools.insider_sales import insider_sales
from src.tools.insider_clusters import insider_clusters

# real-shaped Form 4 XML (structure copied from an actual EDGAR filing)
FORM4_XML = b"""<?xml version="1.0"?>
<ownershipDocument>
  <documentType>4</documentType>
  <issuer><issuerName>Apple Inc.</issuerName></issuer>
  <reportingOwner>
    <reportingOwnerId><rptOwnerName>Newstead Jennifer</rptOwnerName></reportingOwnerId>
  </reportingOwner>
  <nonDerivativeTable>
    <nonDerivativeTransaction>
      <transactionDate><value>2026-11-24</value></transactionDate>
      <transactionCoding><transactionCode>S</transactionCode></transactionCoding>
      <transactionAmounts>
        <transactionShares><value>2398</value></transactionShares>
        <transactionPricePerShare><value>347.56</value></transactionPricePerShare>
      </transactionAmounts>
    </nonDerivativeTransaction>
    <nonDerivativeTransaction>
      <transactionDate><value>2026-11-24</value></transactionDate>
      <transactionCoding><transactionCode>M</transactionCode></transactionCoding>
      <transactionAmounts>
        <transactionShares><value>5000</value></transactionShares>
        <transactionPricePerShare><value>0</value></transactionPricePerShare>
      </transactionAmounts>
    </nonDerivativeTransaction>
  </nonDerivativeTable>
</ownershipDocument>
"""


def test_parse_form4_real_shape():
    issuer, rows, base = edgar._parse_form4(FORM4_XML, "https://example/")
    assert issuer == "Apple Inc."
    # both transactions parsed (S + M); code filter happens in the tool
    assert len(rows) == 2
    s = [r for r in rows if r[2] == "S"]
    assert s and s[0][0] == "Newstead Jennifer"
    assert s[0][1] == "2026-11-24" and s[0][3] == 2398.0 and s[0][4] == 347.56


def test_parse_form4_derivative_table():
    xml = FORM4_XML.replace(b"nonDerivativeTable", b"derivativeTable") \
                   .replace(b"nonDerivativeTransaction", b"derivativeTransaction")
    issuer, rows, _ = edgar._parse_form4(xml, "https://example/")
    assert len(rows) == 2


def test_insider_sales_filters_code_s(monkeypatch):
    monkeypatch.setattr(edgar, "resolve_cik", lambda t: "0000320193")
    monkeypatch.setattr(edgar, "recent_filings",
                        lambda cik, form, since: [("0001-26-1", "2026-11-25", "doc.htm")])
    monkeypatch.setattr(edgar, "form4_transactions_doc",
                        lambda cik, acc, doc: edgar._parse_form4(FORM4_XML, "https://src/"))
    out = insider_sales("AAPL", days=30)
    assert out["dataQuality"] == "live"
    sales = out["data"]["sales"]
    assert len(sales) == 1 and sales[0]["shares"] == 2398.0
    assert sales[0]["source"] == "https://src/"


def test_insider_clusters_ranks_and_empty(monkeypatch):
    def fake_resolve(t):
        return "CIK-" + t
    monkeypatch.setattr(edgar, "resolve_cik", fake_resolve)
    monkeypatch.setattr(edgar, "recent_filings",
                        lambda cik, form, since: [("a", "2026-11-25", "d")])
    monkeypatch.setattr(edgar, "form4_transactions_doc",
                        lambda cik, acc, doc: edgar._parse_form4(FORM4_XML, "https://src/"))
    # one seller only -> below default threshold -> empty, with honest note
    out = insider_clusters(tickers=["AAPL"], days=30)
    assert out["data"]["clusters"] == []
    assert out["data"]["emptyResultNote"]