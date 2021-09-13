#!/bin/bash

# install swagger-cli: npm install -g swagger-cli
# install datamodel-codegen: pip3 install datamodel-code-generator
swagger-cli bundle openapi.yaml | datamodel-codegen --input-file-type openapi --enum-field-as-literal one
