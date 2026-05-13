# Regras de Negócio e Lógica de Alertas

## Classificação de tendência
- `bullish_continuation`: tendência alta + score>70 + confirmações cruzadas positivas
- `bearish_continuation`: tendência baixa + score<30 + confirmações cruzadas negativas
- `bullish_reversal`: tendência prévia de baixa + momentum de alta + divergência positiva
- `bearish_reversal`: tendência prévia de alta + momentum de baixa + divergência negativa
- `neutral_indecision`: sinais conflitantes/ADX baixo

## Regras-chave
1. **Confirmação compradora no ouro**
   - DXY queda forte, US10Y queda, BCOM/metais sobem, XAU acelera
2. **Pressão vendedora no ouro**
   - DXY sobe forte, US10Y sobe, metais enfraquecem, XAU perde VWAP
3. **Desacoplamento macro**
   - XAU sobe sem confirmação de pares correlatos
4. **Volatilidade crítica**
   - ATR z-score > limiar + aumento abrupto de range

## Níveis de relevância
- baixo / médio / alto / crítico
com base em magnitude, alinhamento multivariável e persistência temporal
