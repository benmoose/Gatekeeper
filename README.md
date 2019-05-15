# Gatekeeper

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Gatekeeper is Travelbear's authentication server.

#### Quickstart

Docker is recommended for local development.

With it installed, you can use the scripts in `dev/` to run common commands
- `dev/test.sh [pytest-args]` · run the test suite, all arguments are passed through to pytest
- `dev/manage.sh [command]` · run a Django management command
- `dev/fmt.sh [--check]` · lint Python code
- `dev/psql.sh` · run psql on the DB container, the DB container needs to be running for this command to work

To run a local version of the production app with Django served with gunicorn behind Nginx run
```bash
$ docker-compose up
```

The service listens at [http://localhost:8000](http://localhost:8000).
