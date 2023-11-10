VENV = .venv
BIN = $(VENV)/bin

.PHONY: venv
venv:
	python3.12 -m venv $(VENV)

.PHONY: deps
deps: venv
	$(BIN)/pip install -r requirements.txt

.PHONY: deps-dev
deps-dev:
	$(BIN)/pip install -r requirements_dev.txt
	$(MAKE) deps

.PHONY: fmt
fmt: deps-dev
	$(BIN)/black .
	$(BIN)/isort .

.PHONY: lint
lint: deps-dev
	$(BIN)/isort --check .
	$(BIN)/black --check .
	$(BIN)/flake8 .
	$(BIN)/pyright .

.PHONY: test
test: deps-dev
	$(BIN)/pytest .

.PHONY: qa
qa: lint test
