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

COPY pyproject.toml .flake8 Makefile /build
COPY src /build/src
COPY tests /build/tests

RUN pip wheel --wheel-dir=/opt/wheelhouse-prod . \
    && pip wheel --wheel-dir=/opt/wheelhouse-prod 'setuptools==69.0.2' 'wheel==0.42.0' \
    && make venv \
    && /build/.venv/bin/pip install --find-links=/opt/wheelhouse-prod '.[dev]'
RUN make qa

FROM base as final

RUN mkdir /opt/notifier

COPY --from=builder /opt/wheelhouse-prod /opt/wheelhouse-prod
COPY --from=builder /build/pyproject.toml /opt/notifier/pyproject.toml
COPY --from=builder /build/src /opt/notifier/src

RUN pip install --no-index --find-links=/opt/wheelhouse-prod /opt/notifier

ENTRYPOINT ["notify"]
CMD ["--help"]
