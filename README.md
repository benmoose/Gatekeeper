# 🔒 Gatekeeper

[![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/benmoose/gatekeeper)](https://cloud.docker.com/repository/docker/benmoose/gatekeeper)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Gatekeeper is open source, lightweight JWT-based authentication server for passwordless
SMS phone verification.
Users signup to your service by entering an SMS code, generating an access token which
can be verified by your application without requiring database lookups.
Persistent sessions are supported with refresh tokens.

### Usage

Gatekeeper is open source, so feel free to host the project on your own servers.
Alternatively, it's available as a Docker image.

#### Gatekeeper Docker image

A quick way to get up and running is to use the Gatekeeper Docker image,
which lives on Docker Hub at [`benmoose/gatekeeper`](https://cloud.docker.com/repository/docker/benmoose/gatekeeper).

You can configure the image with environment variables:
- `ENVIRONMENT` should be one of `"production", "staging" or "test"`
- `DB_HOST` database hostname
- `DB_PORT` database port
- `DB_NAME` database name
- `DB_USER` username of the database user to connect to
- `DB_PASSWORD` corresponding password for the user
- `AUTH_PUBLIC_KEY_PATH` path to the public key to verify tokens
- `AUTH_PRIVATE_KEY_PATH` path to the private key to sign tokens
- `AUTH_ACCESS_TOKEN_AUDIENCE` value to populate the `aud=` claim in the JWT
- `AUTH_ACCESS_TOKEN_ISSUER` value to populate the `iss=` claim in the JWT
- `TWILIO_ACCOUNT_SID` your Twilio account SID
- `TWILIO_AUTH_TOKEN` your Twilio auth token
- `TWILIO_MESSAGING_SERVICE_SID` your Twilio messaging service SID _optional_
- `TWILIO_MESSAGE_STATUS_CALLBACK` URL to which Twilio will send SMS status webhook requests _optional_

Alongside Gatekeeper, you will need a database (e.g. Postgres) and a web server (e.g. Nginx).
The easiest way to set this up locally is to use docker-compose.
A minimal `docker-compose.yml` might look like this.

**Note:** Gatekeeper only supports postgres databases at the moment.

```yaml
version: '3'

services:
  db:
    image: postgres

  gatekeeper:
    image: benmoose/gatekeeper
    # Gatekeeper listens for incoming requests at unix socket `/var/tmp/shared-mount/gunicorn.sock`
    volumes:
      - "shared-mount:/var/tmp/shared-mount"
    environment:
      - "ENVIRONMENT=development"
      - "DB_HOST=db"
      - "DB_NAME=postgres"
      - "DB_USER=postgres"
      - "DB_PASSWORD="
    depends_on:
      - db
    
  nginx:
    image: benmoose/gatekeeper-nginx
    volumes:
      - "shared-mount:/var/tmp/shared-mount"  # enable Nginx to send requests to Gatekeeper
    ports:
      - "8000:80"  # expose to the host on port 8000
    depends_on:
      - gatekeeper

volumes:
  shared-mount:
```

Run `docker-compose up` to start the services.
Call `curl http://localhost:8000/v1/health/` to check Gatekeeper is setup and running.

Gatekeeper listens for incoming requests at unix socket `/var/tmp/shared-mount/gunicorn.sock` so
when configuring your containers ensure that `/var/tmp/shared-mount/gunicorn.sock`
is shared between Gatekeeper and Nginx.
This lets the containers communicate. In the example above, this is achieved with volumes.

`benmoose/gatekeeper-nginx` is an Nginx image configured to use the unix socket at `/var/tmp/shared-mount/gunicorn.sock`.
You can see the configuration file in [operations/nginx/nginx.conf](/operations/nginx/nginx.conf).

### Contributing

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
