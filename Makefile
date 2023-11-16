VENV = .venv
BIN = $(VENV)/bin

.PHONY: venv
venv:
	python3.12 -m venv $(VENV)

.PHONY: deps
deps: venv
	$(BIN)/pip install -r requirements.txt

.PHONY: dev-deps
dev-deps:
	$(BIN)/pip install -r requirements_dev.txt
	$(MAKE) deps

.PHONY: fmt
fmt: dev-deps
	$(BIN)/black .
	$(BIN)/isort .

.PHONY: lint
lint: dev-deps
	$(BIN)/isort --check .
	$(BIN)/black --check .
	$(BIN)/flake8 .
	$(BIN)/pyright --project pyproject.toml .

.PHONY: test
test: dev-deps
	$(BIN)/pytest --cov --cov-report html --cov-report term-missing .

.PHONY: qa
qa: lint test
