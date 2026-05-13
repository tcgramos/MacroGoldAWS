from pydantic import BaseModel
from datetime import datetime

class AssetSignal(BaseModel):
    price: float
    pct_change: float
    momentum: float
    volatility: float

class MacroSnapshot(BaseModel):
    timestamp: datetime
    xauusd: AssetSignal
    dxy: AssetSignal
    us10y: AssetSignal
    bcom: AssetSignal
    silver: AssetSignal
    copper: AssetSignal
    platinum: AssetSignal
    fed_rate_expectation: float

class AlertEvent(BaseModel):
    level: str
    message: str
    reason: str
    visual_confirmation: bool
    interpretation_hint: str
