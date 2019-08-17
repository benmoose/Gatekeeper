# Gatekeeper

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Gatekeeper is open source, lightweight JWT-based authentication server for passwordless
SMS phone verification.
Users signup to your service by entering an SMS code, generating an access token which
can be verified by your application without requiring database lookups.
Persistent sessions are supported with refresh tokens.

### Self Hosting

You can run Gatekeeper from a Docker container or as a standard Django app.

The easiest way to get started is to pull the Gatekeeper image from `benmoose/gatekeeper`. 
Alternatively, you might build your own image from this repository, or run the app directly
on a server without Docker at all.

#### Gatekeeper Docker Image

The official Gatekeeper image lives on Docker Hub.

```bash
docker pull benmoose/gatekeeper
```

The quickest way to get started is to pull that image and expose it to the internet from
behind a web server (e.g. Nginx).

The Gatekeeper image can be configured with environment variables:
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
- `TWILIO_ACCOUNT_SID` Twilio account SID
- `TWILIO_AUTH_TOKEN` Twilio auth token
- `TWILIO_MESSAGING_SERVICE_SID` Twilio messaging service SID
- `TWILIO_MESSAGE_STATUS_CALLBACK` URL to which Twilio will send SMS status webhook requests

##### Configuring Gatekeeper with Nginx

The Gatekeeper image listens for incoming requests at unix socket `/var/tmp/shared-mount/gunicorn.sock`.
You'll need to configure Nginx to send requests to that unix socket.

```
http {
    upstream gatekeeper {
        server unix:/var/tmp/shared-mount/gunicorn.sock;
    }
    
    server {
        location / {
            proxy_pass  http://gatekeeper;
        }
    }
}
```

There's a full reference nginx.conf at [`operations/nginx/nginx.conf`](/operations/nginx/nginx.conf).

With Nginx configured, an minimal working docker-compose file could look something like this.

```yaml
version: '3'
services:
  db:
    image: postgres

  gatekeeper:
    image: benmoose/gatekeeper
    volumes:
      - "shared-mount:/var/tmp/shared-mount"
    environment:
      - "ENVIRONMENT=development"
      - "DB_NAME=postgres"
      - "DB_USER=postgres"
      - "DB_PASSWORD="
      - "DB_HOST=db"
    depends_on:
      - db

  nginx:
    build:
      context: .
      dockerfile: nginx.Dockerfile
    volumes:
      - "shared-mount:/var/tmp/shared-mount"
    ports:
      - "8000:80"
    depends_on:
      - gatekeeper

volumes:
  shared-mount:
```

When configuring your docker containers, ensure that `/var/tmp/shared-mount/gunicorn.sock`
is shared between Gatekeeper and Nginx, so the containers can communicate. In the example above,
this is achieved with volumes.

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
