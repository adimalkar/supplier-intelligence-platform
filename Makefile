.PHONY: help setup proto db-up db-migrate db-seed kafka-up api simulator airflow dashboard up down test lint clean

SHELL := /bin/bash
PROJECT_ROOT := $(shell pwd)
PYTHON := python3

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Help
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Setup
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
setup: ## Install all dependencies + compile protos
	pip install -e ".[all]"
	$(MAKE) proto
	@echo "✅ Setup complete"

setup-api: ## Install API dependencies only
	pip install -e ".[api,dev]"
	$(MAKE) proto

setup-pipeline: ## Install pipeline dependencies only
	pip install -e ".[pipeline,dev]"

setup-cv: ## Install CV dependencies only
	pip install -e ".[cv,dev]"

setup-ai: ## Install AI dependencies only
	pip install -e ".[ai,dev]"

setup-dashboard: ## Install dashboard dependencies only
	pip install -e ".[dashboard,dev]"

setup-simulator: ## Install simulator dependencies only
	pip install -e ".[simulator,dev]"
	$(MAKE) proto

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Protobuf
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
proto: ## Compile protobuf stubs
	$(PYTHON) -m grpc_tools.protoc \
		-I src/edge_simulator/proto \
		--python_out=src/edge_simulator/proto \
		--grpc_python_out=src/edge_simulator/proto \
		--pyi_out=src/edge_simulator/proto \
		src/edge_simulator/proto/telemetry.proto
	@# Fix absolute import to relative import in generated grpc stub
	sed -i 's/import telemetry_pb2 as telemetry__pb2/from . import telemetry_pb2 as telemetry__pb2/' src/edge_simulator/proto/telemetry_pb2_grpc.py
	@# Copy stubs to ingestion_api for the server side
	cp src/edge_simulator/proto/telemetry_pb2.py src/ingestion_api/proto/
	cp src/edge_simulator/proto/telemetry_pb2_grpc.py src/ingestion_api/proto/
	cp src/edge_simulator/proto/telemetry_pb2.pyi src/ingestion_api/proto/ 2>/dev/null || true
	@echo "✅ Proto stubs compiled and copied"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Docker Infrastructure
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
db-up: ## Start PostgreSQL + TimescaleDB
	docker compose up -d postgres
	@echo "⏳ Waiting for PostgreSQL to be ready..."
	@sleep 5
	@echo "✅ PostgreSQL is up"

kafka-up: ## Start Kafka (KRaft mode)
	docker compose up -d kafka kafka-ui
	@echo "⏳ Waiting for Kafka to be ready..."
	@sleep 10
	@echo "✅ Kafka is up"

airflow-up: ## Start Airflow (webserver + scheduler)
	docker compose up -d airflow-init airflow-webserver airflow-scheduler
	@echo "✅ Airflow is up"

infra-up: db-up kafka-up ## Start all infrastructure (DB + Kafka)
	@echo "✅ All infrastructure is up"

up: ## Start everything
	docker compose up -d
	@echo "⏳ Waiting for services to stabilize..."
	@sleep 15
	@echo "✅ All services are up"

down: ## Stop everything
	docker compose down
	@echo "✅ All services stopped"

down-clean: ## Stop everything and remove volumes
	docker compose down -v
	@echo "✅ All services stopped and volumes removed"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Database Management
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
db-migrate: ## Run Alembic migrations
	cd db && alembic upgrade head
	@echo "✅ Migrations applied"

db-rollback: ## Rollback last migration
	cd db && alembic downgrade -1
	@echo "✅ Last migration rolled back"

db-seed: ## Seed initial data
	$(PYTHON) -m db.seed.seed_data
	@echo "✅ Seed data loaded"

db-reset: ## Reset DB (drop all, re-migrate, re-seed)
	cd db && alembic downgrade base
	cd db && alembic upgrade head
	$(PYTHON) -m db.seed.seed_data
	@echo "✅ Database reset complete"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Services (for local development)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
api: ## Start FastAPI ingestion server
	uvicorn src.ingestion_api.main:app --host 0.0.0.0 --port 8000 --reload

simulator: ## Start edge simulators (all suppliers)
	$(PYTHON) -m src.edge_simulator.main --suppliers all --speed 1.0

dashboard: ## Start Streamlit dashboard
	streamlit run src/dashboard/app.py --server.port 8501

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Quality
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
test: ## Run all tests
	pytest tests/ -v --cov=src --cov-report=term-missing

test-unit: ## Run unit tests only
	pytest tests/unit/ -v -m unit

test-integration: ## Run integration tests only
	pytest tests/integration/ -v -m integration

test-e2e: ## Run end-to-end tests
	pytest tests/e2e/ -v -m e2e

lint: ## Run linter + type checker
	ruff check src/ tests/
	ruff format --check src/ tests/
	mypy src/

lint-fix: ## Auto-fix lint issues
	ruff check --fix src/ tests/
	ruff format src/ tests/

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Cleanup
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/ htmlcov/ .coverage coverage.xml
	@echo "✅ Cleaned"
