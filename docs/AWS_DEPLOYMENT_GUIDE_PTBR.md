# Manual Completo (Leigo) — Publicar o MacroGoldAWS na AWS

> Guia passo a passo para colocar o projeto em produção com **ECS Fargate + RDS + ElastiCache + ALB + Route53 + ACM**.

---

## 0) Visão geral (o que você vai criar)
Você terá os seguintes blocos:
1. **ECR**: repositório das imagens Docker (frontend e backend).
2. **ECS Fargate**: onde os containers vão rodar.
3. **RDS PostgreSQL**: banco de dados gerenciado.
4. **ElastiCache Redis**: cache/tempo real.
5. **ALB (Load Balancer)**: distribui tráfego HTTPS.
6. **ACM**: certificado SSL grátis (cadeado HTTPS).
7. **Route 53**: domínio apontando para o ALB.
8. **CloudWatch**: logs e monitoramento.
9. **Secrets Manager**: guardar senhas e tokens.

---

## 1) Pré-requisitos

### 1.1 Conta e segurança
- Conta AWS ativa.
- Usuário IAM administrativo (evite root).
- Região recomendada: `us-east-1` (N. Virginia).

### 1.2 Ferramentas no seu computador
Instale:
- Docker Desktop
- AWS CLI v2
- Git

Comandos para validar:
```bash
docker --version
aws --version
git --version
```

### 1.3 Configurar AWS CLI
```bash
aws configure
```
Preencha:
- AWS Access Key ID
- AWS Secret Access Key
- Default region name: `us-east-1`
- Default output format: `json`

Teste:
```bash
aws sts get-caller-identity
```

---

## 2) Subir localmente (teste rápido)
No diretório do projeto:
```bash
docker compose up --build
```
Verifique:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000/docs`

Se isso abrir, o projeto está apto para ir para AWS.

---

## 3) Criar repositórios ECR (frontend e backend)

```bash
aws ecr create-repository --repository-name macrogold/frontend
aws ecr create-repository --repository-name macrogold/backend
```

Guarde os URIs retornados (algo como):
- `123456789012.dkr.ecr.us-east-1.amazonaws.com/macrogold/frontend`
- `123456789012.dkr.ecr.us-east-1.amazonaws.com/macrogold/backend`

Login no ECR:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
```

---

## 4) Build e push das imagens Docker

### 4.1 Frontend
```bash
docker build -t macrogold-frontend ./frontend
docker tag macrogold-frontend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/macrogold/frontend:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/macrogold/frontend:latest
```

### 4.2 Backend
```bash
docker build -t macrogold-backend ./backend
docker tag macrogold-backend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/macrogold/backend:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/macrogold/backend:latest
```

---

## 5) Criar rede base (VPC)
Você pode usar o assistente da AWS:
- Console AWS → **VPC** → **Create VPC** → “VPC and more”.

Crie:
- 2 subnets públicas (ALB)
- 2 subnets privadas (ECS, RDS, Redis)
- NAT Gateway habilitado

Anote:
- VPC ID
- Subnet IDs públicas e privadas

---

## 6) Criar banco RDS (PostgreSQL)

1. Console AWS → RDS → Create database.
2. Engine: PostgreSQL 16.
3. Template: Production (ou Dev/Test no início).
4. DB instance identifier: `macrogold-db`.
5. Username: `postgres`.
6. Password: crie senha forte.
7. Connectivity: VPC criada.
8. **Não deixar público**.
9. Crie Security Group permitindo **5432** apenas do SG do ECS.

No final, copie o endpoint RDS (ex.: `macrogold-db.xxxxxx.us-east-1.rds.amazonaws.com`).

---

## 7) Criar Redis (ElastiCache)

1. Console AWS → ElastiCache → Redis OSS → Create.
2. Nome: `macrogold-redis`.
3. Mesma VPC.
4. Subnets privadas.
5. Security Group liberando 6379 apenas para ECS.

Copie endpoint Redis.

---

## 8) Guardar segredos no Secrets Manager

Crie segredos:
- `macrogold/prod/database_url`
- `macrogold/prod/redis_url`
- `macrogold/prod/telegram_token` (quando integrar)

Exemplo de `database_url`:
```text
postgresql://postgres:SENHA@macrogold-db.xxxxxx.us-east-1.rds.amazonaws.com:5432/macrogold
```

Exemplo de `redis_url`:
```text
redis://macrogold-redis.xxxxxx.0001.use1.cache.amazonaws.com:6379/0
```

---

## 9) Criar Cluster ECS Fargate

1. ECS → Clusters → Create cluster.
2. Tipo: “Networking only (Fargate)”.
3. Nome: `macrogold-cluster`.

### 9.1 Task Definition (backend)
- Launch type: Fargate
- CPU/Memória inicial: 0.5 vCPU / 1GB
- Container image: URI ECR backend
- Port mapping: 8000
- Variáveis ambiente:
  - `DATABASE_URL` via Secrets Manager
  - `REDIS_URL` via Secrets Manager

### 9.2 Task Definition (frontend)
- Image: URI ECR frontend
- Port: 3000
- Env:
  - `NEXT_PUBLIC_API_URL=https://api.seudominio.com` (ou domínio do ALB/API)

---

## 10) Criar Load Balancer (ALB)

1. EC2 → Load Balancers → Create Application Load Balancer.
2. Internet-facing.
3. Subnets públicas.
4. Crie dois target groups:
   - `tg-macrogold-frontend` (porta 3000)
   - `tg-macrogold-backend` (porta 8000)
5. Listener rules:
   - `/api/*` → backend
   - `/*` → frontend

---

## 11) HTTPS com ACM + domínio Route 53

### 11.1 Certificado
- ACM → Request certificate
- Nome: `app.seudominio.com` (e opcional `api.seudominio.com`)
- Validação DNS

### 11.2 DNS
- Route 53 hosted zone do seu domínio
- Criar registro A (Alias) apontando para ALB

### 11.3 Listener HTTPS
- No ALB, adicionar listener 443 com certificado ACM
- Redirecionar HTTP 80 → HTTPS 443

---

## 12) Criar serviços ECS

Crie 2 services no cluster:

### 12.1 `macrogold-backend-svc`
- Task definition backend
- Desired tasks: 2
- Subnets privadas
- SG permitindo tráfego do ALB
- Attach ao `tg-macrogold-backend`

### 12.2 `macrogold-frontend-svc`
- Task definition frontend
- Desired tasks: 2
- Subnets privadas
- SG permitindo tráfego do ALB
- Attach ao `tg-macrogold-frontend`

---

## 13) Logs e monitoramento

1. CloudWatch Logs:
   - Configure logs nos containers
   - Grupos:
     - `/ecs/macrogold/frontend`
     - `/ecs/macrogold/backend`
2. CloudWatch Alarms:
   - CPU alta ECS
   - Memory alta ECS
   - Erros 5XX ALB
3. SNS para alertas por e-mail.

---

## 14) Deploy contínuo (opcional recomendado)

Use GitHub Actions + OIDC:
1. Push no `main`.
2. Pipeline builda imagem.
3. Push no ECR.
4. Atualiza task definition.
5. Força novo deploy ECS.

---

## 15) Checklist final de produção

- [ ] Frontend abre em HTTPS
- [ ] Backend responde `/v1/health`
- [ ] ECS com 2 tasks por serviço
- [ ] RDS sem acesso público
- [ ] Redis privado
- [ ] Segredos no Secrets Manager
- [ ] Alertas CloudWatch ativos
- [ ] Backup RDS habilitado
- [ ] Auto Scaling configurado

---

## 16) Custos iniciais (estimativa)
Para ambiente pequeno/profissional inicial:
- ECS Fargate (2 serviços): custo variável por vCPU/RAM/hora
- RDS PostgreSQL (db.t4g.small ou similar)
- ElastiCache (cache.t4g.micro/small)
- ALB + transferência
- CloudWatch + Route53

Sugestão: começar em modo controlado e escalar conforme uso real.

---

## 17) Próximo passo técnico recomendado
Após publicar:
1. Integrar provedores reais de preço/tick (WebSocket/API institucional).
2. Persistir ticks no PostgreSQL e snapshots no Redis.
3. Implementar worker analítico com indicadores EMA/VWAP/ATR/RSI/MACD/ADX.
4. Ligar alertas Telegram/email/push.
5. Adicionar autenticação, perfil de risco e preferências por usuário.

---

## 18) Solução de problemas comuns

### “Task parando sozinha”
- Veja CloudWatch logs do container.
- Normalmente é env var faltando (DATABASE_URL/REDIS_URL).

### “502 Bad Gateway no ALB”
- Porta errada no target group.
- Health check path incorreto.

### “Frontend abre, mas API não responde”
- `NEXT_PUBLIC_API_URL` errado.
- Regra do listener `/api/*` não aponta para backend.

### “Banco não conecta”
- Security Group do RDS não permite SG do ECS.
- URL do banco com senha/host incorretos.
