# Versão para Heroku (Heroku) — Passo a Passo

> Sim, é possível publicar uma versão alternativa deste sistema no **Heroku**.

## Arquitetura recomendada no Heroku
Para simplificar e manter custo baixo:
- **App 1 (API)**: FastAPI (este repositório já preparado)
- **Banco**: Heroku Postgres
- **Cache**: Heroku Redis
- **Frontend**: opcionalmente em Vercel/Netlify (recomendado) ou segundo app Heroku

---

## 1) O que foi adaptado neste repositório
- `Procfile` para iniciar o serviço web FastAPI via porta dinâmica `$PORT`.
- `runtime.txt` com versão Python.
- `app.json` com blueprint de deploy + addons Postgres/Redis.
- `backend/requirements-heroku.txt` para ambiente Heroku com `gunicorn`.

---

## 2) Pré-requisitos
1. Conta no Heroku
2. Heroku CLI instalado
3. Git instalado

Login:
```bash
heroku login
```

---

## 3) Criar app e addons
No diretório do projeto:
```bash
heroku create macrogold-api
heroku addons:create heroku-postgresql:essential-0 -a macrogold-api
heroku addons:create heroku-redis:mini -a macrogold-api
```

---

## 4) Config vars
Defina variáveis:
```bash
heroku config:set PYTHONPATH=. -a macrogold-api
heroku config:set REDIS_URL=$(heroku config:get REDIS_URL -a macrogold-api) -a macrogold-api
heroku config:set DATABASE_URL=$(heroku config:get DATABASE_URL -a macrogold-api) -a macrogold-api
```

> Observação: Heroku já injeta `DATABASE_URL` e `REDIS_URL`; estes comandos só garantem consistência.

---

## 5) Deploy
```bash
git push heroku HEAD:main
```

Escalar dyno web:
```bash
heroku ps:scale web=1 -a macrogold-api
```

Logs:
```bash
heroku logs --tail -a macrogold-api
```

---

## 6) Testar endpoints
```bash
curl https://macrogold-api.herokuapp.com/v1/health
```

Se retornar `{"status":"ok"}`, está online.

---

## 7) Frontend (duas opções)

### Opção A (recomendada): Frontend fora do Heroku
- Publique Next.js na Vercel
- Configure `NEXT_PUBLIC_API_URL=https://macrogold-api.herokuapp.com`

### Opção B: Frontend em segundo app Heroku
- Criar app `macrogold-web`
- Deploy do diretório `frontend/`
- Definir buildpack Node.js
- Configurar `NEXT_PUBLIC_API_URL`

---

## 8) Escalabilidade mínima no Heroku
- Comece com `standard-1x`
- Ative ao menos 2 dynos web em horários de mercado
- Use Redis para cache de snapshots
- Persistência histórica no Postgres com índices por timestamp

---

## 9) Limitações Heroku (importante)
- Dynos são efêmeros (sem armazenamento local persistente)
- Para WebSocket intenso, monitore limites de conexão
- Custos podem crescer com alta concorrência

Para escala institucional maior, AWS ECS/EKS tende a oferecer melhor custo-controle.

---

## 10) Checklist final
- [ ] App criado no Heroku
- [ ] Postgres conectado
- [ ] Redis conectado
- [ ] `web` dyno ativo
- [ ] `/v1/health` respondendo
- [ ] Frontend apontando para API correta
