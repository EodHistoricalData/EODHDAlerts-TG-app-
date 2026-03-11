# EODHDAlerts-TG-app-

## Workspace Rules
> Part of EODHD ecosystem. Read and follow:
> - `EODHD/the-hitchhikers-guide-to-the-company/docs/rules/general.md` — EODHD general rules
> - Knowledge base: `EODHD/the-hitchhikers-guide-to-the-company/CLAUDE.md`

> 1. [Install Telegram](https:\/\/telegram.org\/apps)

## Tech Stack

Docker,Python

## Development Commands

```bash
# Makefile targets
make build
make docker
make push-sha
make up
make up-dev
make down
make logs

pip install -r requirements.txt

docker compose up -d
```

## Project Structure

```
  scripts/
  strategy/
  Dockerfile
  Makefile
  README.md
  bitbucket-pipelines.yml
  docker-compose.dev.yml
  docker-compose.dev.yml
  docker-compose.yml
  docker-compose.yml
```

## Key Files

- `README.md`
- `.env.example` — environment template
- `docker-compose.yml` — container setup
- `Makefile` — build commands
