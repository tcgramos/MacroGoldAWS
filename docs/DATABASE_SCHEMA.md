# Estrutura de Banco (PostgreSQL)

## Tabelas principais
- `assets` (id, symbol, class, enabled)
- `market_ticks` (id, asset_id, ts, price, volume, bid, ask)
- `market_features` (id, asset_id, ts, ema_fast, ema_slow, vwap, atr, rsi, macd, adx, volatility)
- `correlation_matrix` (id, ts, base_asset, quote_asset, corr_15m, corr_1h, corr_4h)
- `macro_scores` (id, ts, score, regime, confidence)
- `alerts` (id, ts, level, type, title, reason, payload_json, acknowledged)
- `macro_events` (id, ts, event_type, country, impact, description)
- `user_alert_prefs` (id, user_id, min_level, channels_json, quiet_hours_json, sensitivity)

## Índices
- Índices compostos por `(asset_id, ts DESC)`
- Particionamento mensal para `market_ticks`
