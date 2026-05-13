# MacroGoldAWS — Plataforma Institucional de Monitoramento Macroeconômico para XAUUSD

Web app SaaS-ready para monitoramento macro em tempo real com foco em **confirmação de movimento/reversão no ouro (XAUUSD)**, pronto para deploy em AWS.

## Stack (AWS-friendly)
- **Frontend**: Next.js 14 + TypeScript + Tailwind
- **Backend API**: FastAPI + Python 3.11
- **Engine Analítico**: módulo Python dedicado (`services/analytics`)
- **Banco**: PostgreSQL
- **Cache/Stream**: Redis
- **Mensageria/alertas**: Telegram Bot API, Email (SES), Push Web
- **Infra**: Docker, ECS Fargate/EKS, ALB, CloudWatch

## Estrutura do Projeto

```
/frontend                 # Next.js app (dashboard institucional)
/backend                  # FastAPI + regras de negócio + APIs
/infra                    # IaC e templates para AWS
/docs                     # Arquitetura, wireframes, regras, score
/docker-compose.yml       # ambiente local
```

## Como subir localmente

```bash
docker compose up --build
```

Serviços:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Roadmap de Produção (AWS)
1. Containerizar frontend/backend com imagens versionadas no ECR
2. Deploy em ECS Fargate com Auto Scaling
3. RDS PostgreSQL Multi-AZ
4. ElastiCache Redis
5. API Gateway + ALB + WAF
6. Secrets Manager para chaves/API tokens
7. CloudWatch + X-Ray + alarmes SNS

Ver detalhes em [`docs/PRODUCTION_ARCHITECTURE.md`](docs/PRODUCTION_ARCHITECTURE.md).
