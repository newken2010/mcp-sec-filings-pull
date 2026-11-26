import pytest

from src.config import SourceConfig
from src.tools import find_factory, price_compare, moq_check, supplier_verify, shipping_quote, duty_calc, trend_hot


def _cfg() -> SourceConfig:
    return SourceConfig()


def test_envelope_shape_find_factory():
    out = find_factory.find_factory("stainless steel bottle", "Yiwu", 5)
    assert set(out) == {"data", "source", "dataQuality", "disclaimer", "locale"}
    # no creds configured -> degraded, must NOT fabricate suppliers
    assert out["dataQuality"] in ("public", "degraded")
    assert out["data"]["items"] == []


def test_envelope_locale_default_en():
    # correct arg order: (category, region, limit) -> 5 is `limit`, not `region`
    out = find_factory.find_factory("widget", "Yiwu", 5)
    assert out["locale"] == "en"
    assert out["data"]["items"] == []


def test_duty_calc_locale_by_destination():
    # destination DE auto-selects German copy (explicit locale still wins later)
    out = duty_calc.duty_calc("8471.30", "CN", "DE")
    assert out["locale"] == "de"


def test_envelope_price_compare_degrades():
    out = price_compare.price_compare("led strip", 5)
    assert out["data"]["items"] == []
    assert out["disclaimer"] != ""


def test_moq_check_public_fields():
    out = moq_check.moq_check("offer-123")
    assert out["data"]["offer_id"] == "offer-123"
    assert out["data"]["moq"] is None  # not invented
    assert out["dataQuality"] == "degraded"  # no adapter -> no data


def test_supplier_verify_readonly():
    out = supplier_verify.supplier_verify("ABC Co", "Guangdong")
    assert out["data"]["company"] == "ABC Co"
    assert "verify_steps" in out["data"]
    assert out["disclaimer"] != ""


def test_shipping_quote_no_fabricated_price():
    out = shipping_quote.shipping_quote("CN", "US", "sea", 100.0)
    # no logistics key -> degraded, must not invent a price
    assert out["dataQuality"] == "degraded"
    assert out["disclaimer"] != ""


def test_duty_calc_us_hts_live(monkeypatch):
    import src.sources.tariff as t

    class _Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return [{"htsno": "8471.30.01.00", "description": "Portable computers",
                     "general": "Free", "special": "", "other": "35%", "units": ["No."]}]

    monkeypatch.setattr(t.requests, "get", lambda *a, **k: _Resp())
    out = duty_calc.duty_calc("8471.30", "CN", "US")
    assert out["dataQuality"] == "live"
    assert out["source"] == "usitc_hts"
    assert out["data"]["hts_code"] == "8471.30.01.00"
    assert out["data"]["duty_rate_percent"] == 0.0


def test_duty_calc_non_us_degrades():
    out = duty_calc.duty_calc("8471.30", "CN", "DE")
    assert out["dataQuality"] == "degraded"
    assert out["disclaimer"] != ""


def test_duty_calc_degrades_cleanly(monkeypatch):
    # force the USITC call to fail (no network in test) -> degraded
    import src.sources.tariff as t
    import requests as _req

    class _Boom(_req.RequestException):
        pass

    def _raise(*a, **k):
        raise _Boom()

    monkeypatch.setattr("requests.get", _raise)
    out = duty_calc.duty_calc("8471.30", "CN", "US")
    assert out["dataQuality"] == "degraded"
    assert out["disclaimer"] != ""


def test_trend_hot_no_invented_ranking():
    out = trend_hot.trend_hot(None, 5)
    assert out["data"]["items"] == []


def test_all_tools_importable_and_callable():
    for f in (
        find_factory.find_factory,
        price_compare.price_compare,
        moq_check.moq_check,
        supplier_verify.supplier_verify,
        shipping_quote.shipping_quote,
        duty_calc.duty_calc,
        trend_hot.trend_hot,
    ):
        assert callable(f)
