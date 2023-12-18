![CI/CD](https://github.com/bradgwest/job-notifier/actions/workflows/cicd.yaml/badge.svg?event=push)
# Job Notifier

- [Quick Start](#quick-start)
  - [Docker](#docker)
  - [Source](#source)
  - [Development](#development)

## Quick Start

### Docker

**Prerequisites**
* [`docker`](https://docs.docker.com/get-docker/)

```sh
docker run ghcr.io/bradgwest/job-notifier
```

### Source

**Prerequisites**
* [`make`](https://www.gnu.org/software/make/)
* [`python3.12`](https://www.python.org/downloads/)

Install the package:

```sh
make install
```

Run it:

```sh
notify -h
```

### Development

See the [`Makefile`](./Makefile) for helpful development targets.
