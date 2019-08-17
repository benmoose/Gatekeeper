# Gatekeeper

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Gatekeeper is lightweight JWT-based authentication server for passwordless SMS phone
verification.
Users signup to your service by entering an SMS code, generating an access token which
can be verified by your application without requiring database lookups.
Persistent sessions are supported with refresh tokens.

#### Contributing

Docker is recommended for local development.

##### Useful Scripts

With it installed, you can use the scripts in `dev/` to run common commands
- `dev/test.sh [pytest-args]` · run the test suite, all arguments are passed through to pytest
- `dev/manage.sh [command]` · run a Django management command
- `dev/fmt.sh [--check]` · lint Python code
- `dev/psql.sh` · run psql on the DB container, the DB container needs to be running for this command to work

##### Running a Local Server

To run a local version of the production app, run

```bash
$ docker-compose up
```

The local server signs and verifies JWTs using the RSA keys in `__fixtures__/`.

Configure the local server (e.g. Twilio credentials) by setting the relevant variables in `.local.env`.
Take care not to commit changes to this file though!

The local server listens at [http://localhost:8000](http://localhost:8000).
You can set a different port by setting the `SERVICE_PORT` environment variable.

```bash
$ SERVICE_PORT=4040 docker-compose up
```
