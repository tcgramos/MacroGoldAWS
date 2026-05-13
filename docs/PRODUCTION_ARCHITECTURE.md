# Arquitetura Completa (AWS)

## 1) Camadas
- **Presentation**: Next.js servido via ECS Fargate (ou S3+CloudFront para estático)
- **API**: FastAPI em ECS Fargate atrás de ALB
- **Analytics Engine**: workers Python assíncronos (ECS Service separado)
- **Data**: RDS PostgreSQL + ElastiCache Redis
- **Streaming**: WebSocket (API Gateway WebSocket ou Socket service)
- **Observability**: CloudWatch Logs/Metrics, alarms SNS

## 2) Fluxo operacional
1. Conectores coletam dados de mercado/macro em baixa latência.
2. Redis recebe ticks e snapshots.
3. Engine calcula indicadores (EMA, ATR, RSI, MACD, ADX, correlação) e score.
4. Rule Engine classifica movimento: continuação/reversão.
5. Alert Dispatcher envia: UI, Telegram, email, push.
6. PostgreSQL persiste histórico, eventos e auditoria.

## 3) Escalabilidade
- Auto Scaling por CPU/memória/lag de fila
- Separação entre API read-heavy e workers compute-heavy
- Redis para cache de consultas de dashboard
- Tabelas particionadas por data para séries temporais

## 4) Segurança
- AWS WAF + Shield
- IAM least privilege
- Secrets Manager
- TLS end-to-end
- Trilhas de auditoria (CloudTrail)
