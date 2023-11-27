VENV = .venv
BIN = $(VENV)/bin

.PHONY: venv
venv:
	python3.12 -m venv $(VENV)

.PHONY: install
install: venv
	$(BIN)/pip install .

.PHONY: dev-install
dev-install: venv
	$(BIN)/pip install -e .[dev]

.PHONY: fmt
fmt: dev-install
	$(BIN)/black .
	$(BIN)/isort .

.PHONY: lint
lint: dev-install
	$(BIN)/isort --check .
	$(BIN)/black --check .
	$(BIN)/flake8 .
	# explicitly specify pythonpath to work around import issues in docker
	$(BIN)/pyright --pythonpath $(BIN)/python --project pyproject.toml .

.PHONY: test
test: dev-install
	$(BIN)/pytest -v --cov --cov-report html --cov-report term-missing .

.PHONY: build
build:
	docker build -t job-notifier .

.PHONY: qa
qa: lint test
