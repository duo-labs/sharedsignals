# py-openid-sse

NOTE: This repo is still a work in progress! Use with caution.

Python tools for working with OpenID's
[Shared Signals and Events Framework](https://openid.net/specs/openid-sse-framework-1_0.html)
as well as the [CAEP standard](https://openid.net/specs/openid-caep-specification-1_0-02.html).

## Openapi
The `transmitter_spec` folder contains OpenAPI 3.0.3 definitions of the endpoints
that an event transmitter should set up in order to enable stream management by
receivers.

To bundle these files into a single yaml file, you can run
```
docker run --rm -v `pwd`/transmitter_spec:/local/input swagger-cli bundle /local/input/openapi.yaml
```

That will output the bundled openapi spec to stdout. You can redirect that output
to a new file if desired.

## Adding License Headers
Using https://github.com/google/addlicense to automatically add license headers.
This tool is open sourced with Apache 2.0 license.
```
docker run --rm -it -v ${PWD}:/src ghcr.io/google/addlicense \
  -f LICENSEHEADER -ignore **/swagger.yaml -ignore **/models.py *
```
This tool can't remove or update license headers, so removing
license headers would need a separate script or manual process.
