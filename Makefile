COMPOSE_URL = https://airflow.apache.org/docs/apache-airflow/3.3.1/docker-compose.yaml

.PHONY: setup build init up down reset logs ps

setup: ## first-time: env file + official compose file
	@test -f .env || cp .env.example .env
	@test -f docker-compose.yaml || curl -LfO $(COMPOSE_URL)
	@echo "Edit .env if needed (Linux: set AIRFLOW_UID to your user id)."

build: ## build the custom Airflow image
	docker build -t grid-airflow:latest .

init: ## one-time Airflow DB migration + admin user
	docker compose up airflow-init

up: ## start everything
	docker compose up -d

down: ## stop, keep data
	docker compose down

reset: ## stop and DELETE all volumes
	docker compose down --volumes --remove-orphans

logs:
	docker compose logs -f --tail=100

ps:
	docker compose ps
