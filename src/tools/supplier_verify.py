from typing import Optional

from ..config import get_config
from ..envelope import envelope
from ..sources import public_web

# Buyer-facing verification steps, per locale. EN is the source of truth.
_VERIFY_STEPS = {
    "en": [
        "Check public business-credit record (credit)",
        "Check customs export record (customs)",
        "Check Alibaba.com trade feedback",
        "Optional: third-party on-site factory audit",
    ],
    "de": [
        "Öffentliches Firmenregister prüfen (credit)",
        "Zoll-/Exportnachweis prüfen (customs)",
        "Alibaba.com-Handelsfeedback prüfen",
        "Optional: externes Onsite-Fabrik-Audit",
    ],
    "fr": [
        "Vérifier l’enregistrement commercial public (credit)",
        "Vérifier les exportations douanières (customs)",
        "Vérifier les avis commerciaux Alibaba.com",
        "Optionnel : audit de site tiers",
    ],
    "es": [
        "Revisar el registro comercial público (credit)",
        "Revisar el registro de exportación aduanal (customs)",
        "Revisar los comentarios comerciales de Alibaba.com",
        "Opcional: auditoría in situ de terceros",
    ],
    "ja": [
        "公開の企業信用記録を確認（credit）",
        "税関輸出記録を確認（customs）",
        "Alibaba.com の取引評価を確認",
        "任意：サードパーティによる現地監査",
    ],
    "ko": [
        "공개된 사업자 신용 기록 확인 (credit)",
        "세관 수출 기록 확인 (customs)",
        "Alibaba.com 거래 평가 확인",
        "선택: 제3자 현장 공장 감사",
    ],
}


def supplier_verify(company: str, region: Optional[str] = None,
                   locale: Optional[str] = None) -> dict:
    """Verify a supplier: public credit / trade-record / listing signals.

    Uses public business-credit + customs export record + Alibaba.com trade
    feedback. No private data stored; verify qualifications independently
    before transacting. `locale` switches buyer-facing copy (default EN).
    """
    from ..envelope import normalize_locale
    cfg = get_config()
    loc = normalize_locale(locale)
    hits = public_web.find_supplier_hits(cfg, company, region, limit=3)
    payload = {
        "company": company,
        "region": region,
        "public_signals": hits,
        "verify_steps": _VERIFY_STEPS.get(loc, _VERIFY_STEPS["en"]),
    }
    quality = "public" if hits.get("available") else "degraded"
    return envelope(payload, source=hits.get("via", "none"), data_quality=quality,
                    locale=locale, locale_key="supplier")
