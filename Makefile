.PHONY: help install install-dev run test test-cov lint clean deploy logs stop restart update

PROJECT_NAME = amnezia-vpn-bot
DEPLOY_DIR = /opt/$(PROJECT_NAME)
SERVICE_NAME = $(PROJECT_NAME)
VENV = venv

help:
	@echo "make install      - создать venv и установить зависимости"
	@echo "make install-dev  - установить зависимости для разработки"
	@echo "make run          - запустить бота"
	@echo "make test         - запустить тесты"
	@echo "make test-cov     - тесты с покрытием"
	@echo "make deploy       - установить systemd-сервис"
	@echo "make logs         - логи сервиса"
	@echo "make restart      - перезапустить"
	@echo "make update       - обновить и перезапустить"
	@echo "make clean        - удалить временные файлы"

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

test-cov:
	./$(VENV)/bin/pip install pytest-cov
	./$(VENV)/bin/pytest --cov=. --cov-report=html --cov-report=term

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache htmlcov .coverage
	rm -f test_vpn_bot.db vpn_bot.db

deploy:
	cp deploy/$(SERVICE_NAME).service /etc/systemd/system/
	systemctl daemon-reload
	systemctl enable $(SERVICE_NAME)
	systemctl restart $(SERVICE_NAME)

logs:
	journalctl -u $(SERVICE_NAME) -f

stop:
	systemctl stop $(SERVICE_NAME)

restart:
	systemctl restart $(SERVICE_NAME)

update:
	git pull
	./$(VENV)/bin/pip install -r requirements.txt
	systemctl restart $(SERVICE_NAME)