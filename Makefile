.PHONY: help install install-dev run test deploy logs stop restart update \
        docker-build docker-up docker-down docker-logs docker-restart docker-shell docker-update

PROJECT_NAME = amnezia-vpn-bot
VENV = venv

help:
	@echo "make install      - создать venv и установить зависимости"
	@echo "make install-dev  - установить зависимости для разработки"
	@echo "make run          - запустить бота"
	@echo "make test         - запустить тесты"
	@echo "make docker-up    - запустить контейнер"
	@echo "make docker-logs  - логи контейнера"
	@echo "make docker-update - обновить и перезапустить"

install:
	python3 -m venv $(VENV)
	./$(VENV)/bin/pip install --upgrade pip
	./$(VENV)/bin/pip install -r requirements.txt

install-dev: install
	./$(VENV)/bin/pip install -r requirements-dev.txt

run:
	./$(VENV)/bin/python main.py

test:
	./$(VENV)/bin/pytest

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache htmlcov .coverage
	rm -f test_vpn_bot.db vpn_bot.db

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-restart:
	docker compose restart

docker-shell:
	docker compose exec amnezia-vpn-bot sh

docker-update:
	docker compose down
	docker compose build --no-cache
	docker compose up -d