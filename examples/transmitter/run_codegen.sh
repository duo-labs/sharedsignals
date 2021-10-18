#!/bin/bash

tmpdir="$(mktemp -d)"
trap 'rm -rf -- "$tmpdir"' EXIT
bundled_yaml="${tmpdir}/bundled.yaml"

docker build -t swagger-cli -<<EOF
FROM node:16-alpine
RUN npm install -g swagger-cli
ENTRYPOINT ["swagger-cli"]
EOF
# Bundle our multi-file yaml into one file
docker run --rm -v ~/src/py-openid-sse/stream_management:/local/input \
    swagger-cli bundle /local/input/openapi.yaml > "${bundled_yaml}"

# Do server yaml generation
docker run --rm -v "${PWD}/swagger_server/swagger":/local/out/flask/swagger_server/swagger \
    -v "${tmpdir}":/local/input \
    swaggerapi/swagger-codegen-cli-v3 generate \
    -i /local/input/bundled.yaml \
    -l python-flask \
    -o /local/out/flask

docker build -t datamodel-codegen -<<EOF
FROM python:3.9-slim-buster
RUN pip install datamodel-code-generator
ENTRYPOINT ["datamodel-codegen"]
EOF
# Generate pydantic models
docker run --rm -v "${PWD}/swagger_server/swagger":/local/input \
    datamodel-codegen --input /local/input/swagger.yaml \
    --enum-field-as-literal one --use-default --strict-nullable \
    --target-python-version 3.9 --use-schema-description \
    --disable-timestamp \
    > swagger_server/models.py
