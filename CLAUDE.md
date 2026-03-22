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

## Bridge AI
Multi-AI orchestrator with 16 providers and 128 skills.

**Model routing (BDRR):** auto-selects best AI by task — cheap models (DeepSeek, Nova) for simple tasks, powerful (GPT-5.4, Claude, Gemini Pro) for complex. Saves budget.

**Skill routing:** 128 domain skills (engineering, sales, finance, legal, marketing, data, design, ops, HR, product) with 100% accuracy.

**Usage:**
- `bridge_smart(topic)` — auto-select model + mode
- `bridge_smart(topic, profile="power")` — force powerful models
- `bridge_council(topic)` — 6 AI council for architecture/strategy
- `bridge_debate(topic)` — pro/con debate for decisions
- `bridge_ask(perplexity, question)` — fact-check with citations
- `bridge_ask(deepseek-r1, question)` — math/logic reasoning
- `bridge_ideas(topic)` — creative brainstorming (7+ AI providers)
- `bridge_dev_loop(topic)` — iterative dev with Writer+Reviewer+Tester

**Brain (filtered):** call `brain_query(project="<project-name>", zone="business")` at session start for cross-project lessons (code patterns, architecture, security only — no personal data).