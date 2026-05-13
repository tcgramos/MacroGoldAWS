# AWS — Guia 100% Clique a Clique (sem terminal)

> Objetivo: publicar o **MacroGoldAWS** na AWS usando apenas o Console, ideal para iniciantes.

---

## Antes de começar
Você vai precisar de:
- Conta AWS ativa
- Domínio (opcional, mas recomendado)
- Projeto no GitHub (para facilitar build/deploy depois)

Região recomendada para iniciar: **US East (N. Virginia) / us-east-1**.

---

## Etapa 1 — Criar a rede (VPC)
1. No Console AWS, pesquise por **VPC**.
2. Clique em **Create VPC**.
3. Escolha **VPC and more**.
4. Defina:
   - Number of AZs: **2**
   - Public subnets: **2**
   - Private subnets: **2**
   - NAT gateways: **1** (ou 2 em produção mais robusta)
5. Clique em **Create VPC**.
6. Anote os IDs da VPC e subnets.

---

## Etapa 2 — Criar Security Groups (firewall)
1. Vá em **EC2 > Security Groups**.
2. Crie os grupos:

### 2.1 `sg-alb`
- Inbound:
  - HTTP 80 de `0.0.0.0/0`
  - HTTPS 443 de `0.0.0.0/0`
- Outbound: All traffic

### 2.2 `sg-ecs-frontend`
- Inbound:
  - TCP 3000 vindo de `sg-alb`
- Outbound: All traffic

### 2.3 `sg-ecs-backend`
- Inbound:
  - TCP 8000 vindo de `sg-alb`
- Outbound: All traffic

### 2.4 `sg-rds`
- Inbound:
  - TCP 5432 vindo de `sg-ecs-backend`
- Outbound: All traffic

### 2.5 `sg-redis`
- Inbound:
  - TCP 6379 vindo de `sg-ecs-backend`
- Outbound: All traffic

---

## Etapa 3 — Criar banco PostgreSQL (RDS)
1. Abra **RDS**.
2. Clique em **Create database**.
3. Selecione:
   - Standard create
   - Engine: **PostgreSQL**
   - Version: 16.x
4. Template: **Production** (ou Dev/Test para economizar).
5. Em Settings:
   - DB instance identifier: `macrogold-db`
   - Master username: `postgres`
   - Password: crie e guarde
6. Em Connectivity:
   - VPC: a criada na Etapa 1
   - Public access: **No**
   - VPC security group: escolha `sg-rds`
7. Clique em **Create database**.
8. Após criar, copie o **Endpoint**.

---

## Etapa 4 — Criar Redis (ElastiCache)
1. Abra **ElastiCache**.
2. Clique em **Create** (Redis OSS).
3. Nome: `macrogold-redis`.
4. Escolha VPC da Etapa 1.
5. Subnets privadas.
6. Security group: `sg-redis`.
7. Clique em **Create**.
8. Copie o endpoint Redis.

---

## Etapa 5 — Criar segredos (Secrets Manager)
1. Abra **Secrets Manager**.
2. Clique em **Store a new secret**.
3. Tipo: **Other type of secret**.
4. Crie os segredos abaixo:

### 5.1 `macrogold/prod/database_url`
Valor:
`postgresql://postgres:SUA_SENHA@ENDPOINT_RDS:5432/macrogold`

### 5.2 `macrogold/prod/redis_url`
Valor:
`redis://ENDPOINT_REDIS:6379/0`

### 5.3 (Opcional) `macrogold/prod/telegram_token`
Valor do bot token.

---

## Etapa 6 — Criar repositórios ECR (pela tela)
1. Abra **ECR**.
2. Clique em **Create repository**.
3. Crie:
   - `macrogold/frontend`
   - `macrogold/backend`
4. Deixe privados (Private).

> Observação: o upload das imagens para ECR normalmente é por terminal/CI. Se quiser 100% sem terminal, no próximo passo usaremos **App Runner** como alternativa simplificada.

---

## Etapa 7 — Opção A (mais profissional): ECS Fargate

### 7.1 Criar cluster
1. Abra **ECS > Clusters**.
2. Clique **Create cluster**.
3. Nome: `macrogold-cluster`.
4. Infra: **AWS Fargate**.
5. Clique em **Create**.

### 7.2 Criar Task Definition — Backend
1. ECS > Task definitions > **Create new task definition**.
2. Launch type: Fargate.
3. Nome: `macrogold-backend-task`.
4. CPU/Memória inicial: 0.5 vCPU / 1 GB.
5. Container:
   - Name: `backend`
   - Image URI: ECR backend
   - Port: 8000
6. Em Environment/Secrets:
   - `DATABASE_URL` (Secrets Manager)
   - `REDIS_URL` (Secrets Manager)
7. Logging:
   - CloudWatch group `/ecs/macrogold/backend`
8. Create.

### 7.3 Criar Task Definition — Frontend
1. Crie nova task definition: `macrogold-frontend-task`.
2. Container:
   - Name: `frontend`
   - Image URI: ECR frontend
   - Port: 3000
3. Env var:
   - `NEXT_PUBLIC_API_URL` = URL da API (depois vamos apontar)
4. Logging:
   - `/ecs/macrogold/frontend`
5. Create.

---

## Etapa 8 — Criar Load Balancer (ALB)
1. Abra **EC2 > Load Balancers**.
2. Clique **Create load balancer** > **Application Load Balancer**.
3. Configure:
   - Scheme: Internet-facing
   - IP type: IPv4
   - VPC: sua VPC
   - Subnets: públicas
   - Security group: `sg-alb`
4. Crie target groups:
   - `tg-macrogold-backend` (HTTP 8000)
   - `tg-macrogold-frontend` (HTTP 3000)
5. Listener inicial:
   - 80 HTTP -> frontend (padrão)
6. Create ALB.

---

## Etapa 9 — Criar serviços ECS
No cluster `macrogold-cluster`:

### 9.1 Serviço backend
1. **Create service**.
2. Task definition: `macrogold-backend-task`.
3. Desired tasks: 2.
4. Subnets: privadas.
5. Security group: `sg-ecs-backend`.
6. Load balancing: `tg-macrogold-backend`.
7. Health check path: `/v1/health`.
8. Create service.

### 9.2 Serviço frontend
1. **Create service**.
2. Task definition: `macrogold-frontend-task`.
3. Desired tasks: 2.
4. Subnets: privadas.
5. Security group: `sg-ecs-frontend`.
6. Load balancing: `tg-macrogold-frontend`.
7. Create service.

---

## Etapa 10 — Regras de rota no ALB
1. No ALB, abra **Listeners and rules**.
2. Edite a regra do listener 80:
   - Se path for `/api/*` -> encaminhar para `tg-macrogold-backend`
   - Caso contrário -> `tg-macrogold-frontend`
3. Salve.

---

## Etapa 11 — HTTPS (cadeado)

### 11.1 Certificado
1. Abra **ACM**.
2. Clique em **Request certificate**.
3. Domínio: `app.seudominio.com` (ou seu domínio real).
4. Validação: DNS.

### 11.2 DNS
1. Abra **Route 53**.
2. Hosted zone do seu domínio.
3. Crie registros de validação que o ACM pedir.
4. Após validar, no ALB crie listener HTTPS 443 com esse certificado.
5. Configure redirect 80 -> 443.

---

## Etapa 12 — Observabilidade
1. Abra **CloudWatch Logs** e confirme logs:
   - `/ecs/macrogold/backend`
   - `/ecs/macrogold/frontend`
2. Em **CloudWatch Alarms**, crie:
   - CPU ECS alta
   - Memória ECS alta
   - ALB 5XX > limiar
3. Opcional: notificações via SNS para e-mail.

---

## Etapa 13 — Teste final (clique a clique)
1. Abra URL do ALB/URL do domínio.
2. Verifique se frontend abre.
3. Teste endpoint de saúde no navegador:
   - `https://SEU_DOMINIO/api/v1/health` (ou ajuste sua regra de proxy)
4. No CloudWatch, confirme logs de requests.

---

## Etapa 14 — Alternativa super simples (App Runner)
Se você achar ECS complexo:
1. Abra **App Runner**.
2. Crie serviço conectando direto ao repositório (GitHub) ou ECR.
3. Publique frontend e backend separadamente.
4. Configure env vars/secrets.
5. Use domínio customizado.

> Prós: muito mais simples para iniciar.
> Contras: menos controle avançado que ECS.

---

## Erros comuns e solução rápida

### Erro 1: 502 no ALB
- Target group com porta errada.
- Health check path inválido.

### Erro 2: Backend não conecta no RDS
- SG do RDS não liberado para `sg-ecs-backend`.
- URL de conexão incorreta no secret.

### Erro 3: Frontend sem dados
- `NEXT_PUBLIC_API_URL` apontando para URL incorreta.
- Regra `/api/*` não roteando para backend.

### Erro 4: Task reiniciando
- Falha de env vars obrigatórias.
- Erro de start do container (ver CloudWatch logs).

---

## Checklist final
- [ ] VPC com subnets pública/privada
- [ ] SGs corretos por camada
- [ ] RDS privado funcionando
- [ ] Redis privado funcionando
- [ ] Secrets criados
- [ ] ECS serviços backend/frontend estáveis
- [ ] ALB roteando `/api/*` para backend
- [ ] HTTPS ativo via ACM
- [ ] Logs e alarms ativos
