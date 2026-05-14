# =========================
# Docker Compose
# =========================

COMPOSE=docker compose -f docker/docker-compose.yaml

# -------------------------
# Core Commands
# -------------------------

up:
	$(COMPOSE) up --build -d 

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) down
	$(COMPOSE) up --build -d 

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

# -------------------------
# Dynamic Service Commands
# -------------------------

service:
	$(COMPOSE) up $(SERVICE) -d 

service-build:
	$(COMPOSE) up --build $(SERVICE) -d 

service-logs:
	$(COMPOSE) logs -f $(SERVICE) 

service-shell:
	$(COMPOSE) exec $(SERVICE) bash

service-stop:
	$(COMPOSE) stop $(SERVICE)

# -------------------------
# dbt Commands
# -------------------------

dbt-docs:
	$(COMPOSE) exec airflow-worker bash -c "cd /opt/airflow/dbt && dbt docs generate && dbt docs serve --host 0.0.0.0 --port 8082"