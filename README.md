![CI/CD](https://github.com/github/docs/actions/workflows/cicd.yml/badge.svg?event=push)

# Job Notifier

## Quick Start

### Docker

Build the image:

```sh
make build
```

Run it:

```sh
docker run job-notifier
```

### From Source

Install dependencies:

```sh
make deps
```

```sh
python -m src.runner -h
```

### Development

```sh
make dev-deps
```
