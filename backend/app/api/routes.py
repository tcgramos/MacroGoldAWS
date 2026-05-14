from fastapi import APIRouter
from app.core.schemas import MacroSnapshot, AlertEvent
from services.analytics.engine import classify_market_state, macro_strength_score

router = APIRouter(prefix="/v1")

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/analyze")
def analyze(snapshot: MacroSnapshot):
    classification = classify_market_state(snapshot)
    score = macro_strength_score(snapshot)
    return {"classification": classification, "macro_strength_score": score}

@router.post("/alerts/simulate", response_model=AlertEvent)
def simulate_alert(snapshot: MacroSnapshot):
    classification = classify_market_state(snapshot)
    score = macro_strength_score(snapshot)

    if score >= 80:
        msg = "CONFIRMAÇÃO DE FORÇA COMPRADORA NO OURO"
        level = "critical"
    elif score <= 20:
        msg = "PRESSÃO VENDEDORA EXTREMA NO OURO"
        level = "critical"
    else:
        msg = "MERCADO EM TRANSIÇÃO / INDECISÃO"
        level = "medium"

    return AlertEvent(
        level=level,
        message=msg,
        reason=f"Classificação={classification}; score={score}",
        visual_confirmation=True,
        interpretation_hint="Valide alinhamento DXY + US10Y + metais correlacionados antes da execução"
    )
