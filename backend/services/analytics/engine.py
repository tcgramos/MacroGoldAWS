from app.core.schemas import MacroSnapshot

def macro_strength_score(s: MacroSnapshot) -> int:
    # Score interpretativo (0-100) com pesos transparentes
    weights = {
        "dxy": -0.20,
        "us10y": -0.20,
        "bcom": 0.15,
        "silver": 0.15,
        "copper": 0.10,
        "platinum": 0.10,
        "xau_momentum": 0.10,
    }

    raw = 50
    raw += s.dxy.pct_change * 100 * weights["dxy"]
    raw += s.us10y.pct_change * 100 * weights["us10y"]
    raw += s.bcom.pct_change * 100 * weights["bcom"]
    raw += s.silver.pct_change * 100 * weights["silver"]
    raw += s.copper.pct_change * 100 * weights["copper"]
    raw += s.platinum.pct_change * 100 * weights["platinum"]
    raw += s.xauusd.momentum * weights["xau_momentum"]

    return max(0, min(100, round(raw)))


def classify_market_state(s: MacroSnapshot) -> str:
    score = macro_strength_score(s)

    if score >= 80:
        return "bullish_continuation"
    if 60 <= score < 80:
        return "bullish_reversal"
    if 40 <= score < 60:
        return "neutral_indecision"
    if 20 <= score < 40:
        return "bearish_reversal"
    return "bearish_continuation"
