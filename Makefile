REPO ?= registry.digitalocean.com/vault33
IMAGE ?= eodhd-tg-bot
TAG ?= local

UID := $(shell id -u)
GID := $(shell id -g)

build:
	docker build -t $(IMAGE):$(TAG) .
	docker image prune --force --filter=label=$(IMAGE) || true

docker:
	docker tag $(IMAGE):$(TAG) $(REPO)/$(IMAGE):latest
	docker push $(REPO)/$(IMAGE):latest

push-sha:
	$(eval GIT_SHA := $(shell git rev-parse --short HEAD))
	docker tag $(IMAGE):$(TAG) $(REPO)/$(IMAGE):$(GIT_SHA)
	docker push $(REPO)/$(IMAGE):$(GIT_SHA)

up:
	USER_ID=$(UID) GROUP_ID=$(GID) docker compose up --force-recreate --remove-orphans --no-start
	USER_ID=$(UID) GROUP_ID=$(GID) docker compose up -d bot

up-dev:
	USER_ID=$(UID) GROUP_ID=$(GID) docker compose -f docker-compose.dev.yml up --build --force-recreate --remove-orphans -d

down:
	docker compose down

logs:
	docker compose logs -f bot
