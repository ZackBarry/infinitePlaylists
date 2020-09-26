.DEFAULT_GOAL := help
.PHONY: help

IMAGE_TAG ?= latest

build: ## Build ETL Docker image.
	@echo "Building image for ETL."
	@IMAGE_TAG=$(IMAGE_TAG) docker-compose build

up: ## Spin up docker-compose stack.
	@echo "Spinning up docker-compose stack."
	@IMAGE_TAG=$(IMAGE_TAG) docker-compose up

down: ## Spin down docker-compose stack.
	@echo "Taking down docker-compose stack."
	@docker-compose down

debug: ## Get a bash shell for the etl service.
	@echo "Spinning up docker-compose stack and opening a bash sell for etl service."
	@IMAGE_TAG=$(IMAGE_TAG) docker-compose \
														-f docker-compose.yml \
														-f docker-compose.debug.yml \
														run etl

help:
	@printf "\033[36m%-30s\033[0m %s\n" "Usage: make [target] [args]"
	@printf "\033[36m%-30s\033[0m %s\n" "Args:"
	@printf "\033[36m%-30s\033[0m %s\n" "    IMAGE_TAG=<tag>: Tag for infinite-playlists image."
	@printf "\033[36m%-30s\033[0m %s\n" "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| sort \
	| awk 'BEGIN{FS=": ## "}; {printf "\033[36m    %-30s\033[0m %s\n", $$1, $$2}'
