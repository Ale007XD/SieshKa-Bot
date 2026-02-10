# Food Delivery Bot Makefile

.PHONY: help build up down logs test migrate backup restore clean prod prod-logs

# Default target
help:
	@echo "Food Delivery Bot - Available commands:"
	@echo "  make build      - Build Docker images"
	@echo "  make up         - Start development environment"
	@echo "  make down       - Stop all containers"
	@echo "  make logs       - View logs"
	@echo "  make test       - Run tests"
	@echo "  make migrate    - Run database migrations"
	@echo "  make backup     - Create database backup"
	@echo "  make restore    - Restore database from backup"
	@echo "  make clean      - Clean up containers and volumes"
	@echo "  make prod       - Start production environment"
	@echo "  make prod-logs  - View production logs"

# Development commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	docker-compose run --rm api pytest tests/ -v

migrate:
	docker-compose run --rm api alembic upgrade head

shell:
	docker-compose run --rm api bash

# Production commands
prod:
	docker-compose -f docker-compose.prod.yml up -d

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

prod-down:
	docker-compose -f docker-compose.prod.yml down

prod-build:
	docker-compose -f docker-compose.prod.yml build

# Backup and restore
backup:
	docker-compose -f docker-compose.prod.yml exec backup /app/scripts/backup/run_backup.sh

restore:
	@echo "Usage: make restore FILE=backup_file.dump.gz"
	@if [ -z "$(FILE)" ]; then \
		echo "Error: FILE parameter required"; \
		exit 1; \
	fi
	docker cp $(FILE) food_delivery_db_prod:/tmp/restore.dump.gz
	docker-compose -f docker-compose.prod.yml exec postgres bash -c "gunzip /tmp/restore.dump.gz && pg_restore -U ${POSTGRES_USER} -d ${POSTGRES_DB} --clean /tmp/restore.dump"

# Cleanup
clean:
	docker-compose down -v
	docker-compose -f docker-compose.prod.yml down -v
	docker system prune -f

# Admin utilities
create-admin:
	docker-compose run --rm api python scripts/create_admin.py $(ARGS)

lint:
	flake8 app/ --max-line-length=100 --exclude=migrations
	black app/ --check

format:
	black app/

# Database utilities
psql:
	docker-compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

redis-cli:
	docker-compose exec redis redis-cli
