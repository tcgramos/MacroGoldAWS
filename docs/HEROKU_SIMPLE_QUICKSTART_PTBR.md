# Heroku Simples (1 app) — Guia Rápido

> Versão mais simples possível: **apenas a API FastAPI** em 1 app Heroku.

## 1) Pré-requisitos
- Conta Heroku
- Heroku CLI
- Git

## 2) Login
```bash
heroku login
```

## 3) Criar app
```bash
heroku create macrogold-api-simples
```

## 4) Adicionar banco e redis
```bash
heroku addons:create heroku-postgresql:essential-0 -a macrogold-api-simples
heroku addons:create heroku-redis:mini -a macrogold-api-simples
```

## 5) Definir variável de path
```bash
heroku config:set PYTHONPATH=. -a macrogold-api-simples
```

## 6) Publicar
```bash
git push heroku HEAD:main
heroku ps:scale web=1 -a macrogold-api-simples
```

## 7) Testar
```bash
heroku open -a macrogold-api-simples
curl https://macrogold-api-simples.herokuapp.com/v1/health
```

Esperado:
```json
{"status":"ok"}
```

## 8) Abrir documentação da API
- `https://macrogold-api-simples.herokuapp.com/docs`

## 9) Deploy com botão (opcional)
Você também pode usar **Deploy to Heroku** (usa `app.json`):

`https://heroku.com/deploy?template=https://github.com/SEU_USUARIO/SEU_REPO`

## 10) Próximo passo recomendado
- Publicar frontend separadamente (Vercel) e apontar para a URL da API Heroku.
