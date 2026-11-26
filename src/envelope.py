"""Shared response envelope + data-quality markers.

Every tool returns a dict with:
  - data:        the payload (list or dict)
  - source:      which data source answered (public_web / usitc_hts / fx_public / degraded)
  - dataQuality: "live" | "public" | "degraded"
  - disclaimer:  compliance note (always present for supplier/tariff data)
  - locale:      output language code (defaults "en")

`degraded` means the preferred source was unavailable and public data was
used; the caller can decide whether to retry or accept.

Buyer-facing copy is EN by default. Pass `locale` (or `destination` for the
tariff/shipping tools) to switch — see `localize`. Non-EN locales degrade to
EN if the translation table has no entry (we never emit broken mixed text).
"""
from typing import Any

SUPPORTED = ("en", "de", "fr", "es", "ja", "ko")
_DEFAULT = "en"


def normalize_locale(locale: str | None, destination: str | None = None) -> str:
    """Pick output locale: explicit `locale` wins; else infer from destination
    country; else default EN. Unknown codes fall back to EN."""
    if locale:
        loc = locale.strip().lower()
        if loc in SUPPORTED:
            return loc
        # accept "de-DE" / "ja_JP" style
        base = loc.split("-")[0].split("_")[0]
        if base in SUPPORTED:
            return base
    if destination:
        dest = destination.strip().upper()
        region_map = {
            "US": "en", "GB": "en", "CA": "en", "AU": "en", "NZ": "en",
            "DE": "de", "AT": "de", "CH": "de",
            "FR": "fr", "BE": "fr",
            "ES": "es", "MX": "es", "AR": "es",
            "JP": "ja",
            "KR": "ko",
        }
        if dest in region_map:
            return region_map[dest]
    return _DEFAULT


# EN source strings (kept public so tools can reference and feed `localize`)
SUPPLIER_EN = (
    "Publicly displayed supplier fields only; no off-platform or private "
    "data stored. Verify qualifications independently before transacting."
)
TARIFF_EN = (
    "Tariff estimate from public USITC HTS sources for planning only; "
    "confirm with a licensed customs broker before shipment."
)
SHIP_EN = (
    "Estimate only; confirm with the carrier before booking."
)
TREND_EN = (
    "Trend signal only; validate against live demand before sourcing."
)

# legacy aliases (pre-rename)
SUPPLIER_DISCLAIMER = SUPPLIER_EN
TARIFF_DISCLAIMER = TARIFF_EN


def localize(text: str, locale: str) -> str:
    """Translate a known copy string. Untranslated entries return the EN text
    so we never emit a half-localised blob. (Translation table is intentionally
    small: disclaimers + degraded guidance. Data fields stay in source language.)"""
    if locale == "en" or text not in _TABLE:
        return text
    return _TABLE[text].get(locale, text)


# EN copy -> {locale: translation}. Keep EN as the source of truth.
_TABLE = {
    SUPPLIER_EN: {
        "de": "Nur öffentlich sichtbare Lieferantenfelder; keine privat- oder plattformfremden Daten gespeichert. Qualifikationen vor Abschluss selbst prüfen.",
        "fr": "Champs fournisseur publics uniquement ; aucune donnée privée ni hors plateforme stockée. Vérifiez les qualifications vous-même avant de conclure.",
        "es": "Solo campos públicos de proveedor; no se almacena datos privados ni de otras plataformas. Verifique las calificaciones antes de transar.",
        "ja": "公開されているサプライヤー情報のみ；プライベート・他プラットフォームのデータは保存しません。取引前に資格を必ずご自身で確認してください。",
        "ko": "공개된 공급자 정보만 사용하며 개인/타 플랫폼 데이터는 저장하지 않습니다. 거래 전 자격을 반드시 직접 확인하세요.",
    },
    TARIFF_EN: {
        "de": "Zollschätzung aus öffentlichen USITC-HTS-Quellen nur zur Planung; vor Versand mit einem lizenzierten Spediteur bestätigen.",
        "fr": "Estimation des droits de douane d’après les sources publiques USITC HTS, à des fins de planification uniquement ; à confirmer avec un transitaire agréé avant expédition.",
        "es": "Estimación arancelaria de fuentes públicas USITC HTS solo para planificación; confirme con un agente aduanal licenciado antes del envío.",
        "ja": "公的なUSITC HTSソースに基づく税関推定値は計画用のみ；出荷前は必ず資格を持つ税関通関業者とご確認ください。",
        "ko": "공개된 USITC HTS 출처 기반 관세 추정치는 계획 용도만이며, 출하 전 면허 통관업자와 반드시 확인하세요.",
    },
    SHIP_EN: {
        "de": "Nur Schätzung; buchen Sie mit dem Spediteur nach.",
        "fr": "Estimation uniquement ; à confirmer avec le transporteur avant réservation.",
        "es": "Solo estimación; confirme con el transportista antes de reservar.",
        "ja": "推定値のみ；手配前に必ず運送会社にご確認ください。",
        "ko": "추정치만입니다. 예약 전 운송업체와 반드시 확인하세요.",
    },
    TREND_EN: {
        "de": "Nur Trendsignal; vor Beschaffung mit Live-Nachfrage validieren.",
        "fr": "Signal de tendance uniquement ; à valider avec la demande réelle avant sourcing.",
        "es": "Solo señal de tendencia; valide contra la demanda real antes de surtir.",
        "ja": "トレンドシグナルのみ；調達は実際に需要を照合してから行ってください。",
        "ko": "트렌드 시그널만입니다. 소싱 전 실제 수요와 반드시 대조하세요.",
    },
}

# map a semantic key -> its EN source string
_TABLE_KEYS = {
    "supplier": SUPPLIER_EN,
    "tariff": TARIFF_EN,
    "shipping": SHIP_EN,
    "trend": TREND_EN,
}


def envelope(data: Any, source: str, data_quality: str, disclaimer: str = "",
             locale: str | None = None, locale_key: str | None = None,
             destination: str | None = None) -> dict:
    """Build the standard response envelope.

    - `locale` / `destination` select the output language (destination is a
      hint for tariff/shipping tools: e.g. "DE" -> German copy).
    - `locale_key` picks a known copy string from `_TABLE_KEYS` when
      `disclaimer` is left empty.
    """
    text = _TABLE_KEYS.get(locale_key, disclaimer) if locale_key else disclaimer
    out_locale = normalize_locale(locale, destination)
    return {
        "data": data,
        "source": source,
        "dataQuality": data_quality,
        "disclaimer": localize(text, out_locale),
        "locale": out_locale,
    }
