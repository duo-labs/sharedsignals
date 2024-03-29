# Example Transmitter
A web server that hosts the Stream Configuration endpoints, as well as a place
to poll for events. Will also create a `/ui` page that shows Swagger documentation
of the OpenAPI spec described in [transmitter_spec](../transmitter_spec/openapi.yaml).

We have added a `/register` endpoint to this service, which is not part of the
Shared Signals spec, because we needed an easy way to create streams and provide
bearer tokens. As the SSF spec continues to evolve, this endpoint may become
unnecessary.
## Overview
This server was generated by the [swagger-codegen](https://github.com/swagger-api/swagger-codegen) project. By using the
[OpenAPI-Spec](https://github.com/swagger-api/swagger-core/wiki) from a remote server, you can easily generate a server stub.  This
is an example of building a swagger-enabled Flask server.

This example uses the [Connexion](https://github.com/zalando/connexion) library on top of Flask.

## Requirements
Python 3.9+

## Run with Docker Compose

From the `examples` directory:
```
docker-compose up transmitter
```
will build an image named `transmitter_1` and run it with development settings (hot-reloading).

## Run with Docker

To run the server on a Docker container, please execute the following from the `examples/transmitter` directory:

```bash
# building the image
docker build -f Dockerfile -t transmitter .

# starting up a container
docker run -p 443:443 -v "${PWD}":/usr/src/app transmitter
```

You can also run tests with docker, if you'd like:
```
docker run --rm -v "${PWD}":/usr/src/app transmitter -m pytest
```

Note that this runs without hot-reloading.

## Run without docker
To run the server, please execute the following from the `examples/transmitter` directory:

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
JWKS_PATH=jwks.json JWK_KEY_ID=key-id python3 -m swagger_server
```

## Environment variables
There are a few environment variables you can set to control how the transmitter
works:

- `FLASK_ENV=development` This will cause the flask server to hot-reload if you change
any code while it is running.
- `JWKS_PATH=/path/to/jwks.json` This specifies where your `jwks.json` file lives.
If you want to use a specific set of keys, you can add them this way. This value
will default to `/usr/keys/jwks.json` and will auto-create a new set of keys on
every run.
- `JWK_KEY_ID=key-id` This specifies which key id in the JWKS you want to use to
encode the SETs. Controlling it with an environment variable allows you to rotate keys
in the JWKS if desired. By default, this will be `transmitter-ES256-001`.

## Usage
To view the Swagger UI open your browser to here:

```
https://localhost/ui/
```

Your Swagger definition lives here:

```
https://localhost/openapi.json
```

Note that because this is a local environment, your browser will warn you that
the https connection is unsafe. You can ignore that warning.

## Development
To launch the integration tests, use tox:
```
pip3 install tox
python3 -m tox
# run only certain tests:
python3 -m tox -- -k test_name_pattern
```



## Codegen

```
./run_codegen
```
Re-generates `swagger.yaml` and `models.py`. Run it from `examples/transmitter`
by running `./run_codegen.sh`
