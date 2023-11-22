FROM python:3.12-slim-bullseye as base

RUN apt-get -qq update \
    && python -m pip install --upgrade pip \
    && apt-get -qq clean \
    && rm -rf /var/lib/apt/lists/*

FROM base as builder

RUN apt-get -qq update \
    && apt-get -qq install -y --no-install-recommends \
        make \
        build-essential \
        nodejs \
    && apt-get -qq clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements*.txt /build/
# cache wheels for later stages
RUN pip wheel --wheel-dir=/opt/wheelhouse-prod -r /build/requirements.txt \
    && pip wheel --wheel-dir=/opt/wheelhouse-dev -r /build/requirements-dev.txt

COPY Makefile /build/
RUN make venv \
    && /build/.venv/bin/pip install --no-index --find-links=/opt/wheelhouse-dev -r /build/requirements-dev.txt \
    && /build/.venv/bin/pip install --no-index --find-links=/opt/wheelhouse-prod -r /build/requirements.txt

COPY pyproject.toml .flake8 /build
COPY src /build/src
COPY tests /build/tests

RUN make qa

FROM base as final

COPY --from=builder /opt/wheelhouse-prod /opt/wheelhouse-prod
COPY --from=builder /build/requirements.txt /opt/requirements.txt

RUN pip install --no-index --find-links=/opt/wheelhouse-prod -r /opt/requirements.txt

COPY --from=builder /build/src src

ENTRYPOINT ["python", "-m", "src.runner"]
CMD ["--help"]
