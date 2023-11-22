VENV = .venv
BIN = $(VENV)/bin

.PHONY: venv
venv:
	python3.12 -m venv $(VENV)

.PHONY: deps
deps: venv
	$(BIN)/pip install -r requirements.txt

.PHONY: dev-deps
dev-deps: venv
	$(BIN)/pip install -r requirements-dev.txt
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
	# explicitly specify pythonpath to work around import issues in docker
	$(BIN)/pyright --pythonpath $(BIN)/python --project pyproject.toml .

.PHONY: test
test: dev-deps
	$(BIN)/pytest -v --cov --cov-report html --cov-report term-missing .

.PHONY: build
build:
	docker build -t job-notifier .

.PHONY: qa
qa: lint test
