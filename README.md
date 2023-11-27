![CI/CD](https://github.com/bradgwest/job-notifier/actions/workflows/cicd.yaml/badge.svg?event=push)
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

### Source

Install dependencies:

```sh
make deps
```

Run it:

```sh
python -m src.runner -h
```

### Development

```sh
make dev-deps
```
