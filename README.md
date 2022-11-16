# SharedSignals

Tools for working with OpenID's
[Shared Signals Framework](https://openid.net/specs/openid-sse-framework-1_0.html).

Please note: The information in this repository reflects the Shared Signals spec
as of November 2021. However, the spec is still evolving. We will continue to make
updates here as the spec changes. Once it is finalized, we will indicate what
version of the spec this code supports.

## sharedsignals.guide
For detailed information about how to work with the transmitters and receivers
described by the Shared Signals Framework, as well as a high level
explanation of what the main concepts are and why you might want to use this
technology, please see our accompanying site [https://sharedsignals.guide](https://sharedsignals.guide).

## Shared Signals Framework Communication Sequence
To understand the communication sequence for SSF, refer to this [document](docs/push-and-poll-events.md).

## Examples
The [examples](examples) folder contains python-based, Dockerized examples
of a transmitter and receiver, as well as a working example of the code demonstrated
on the [https://sharedsignals.guide](https://sharedsignals.guide) website.

Please note that the transmitter and receiver examples here are for education
only and should not be used as production-level code.

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

## Contributing
The work provided here is intended as educational material and as a proof-of-concept.
We welcome further contributions from the open source community.
Please check the [Issues](https://github.com/duo-labs/sharedsignals/issues)
section for ideas about where to start. \
Use [pycodestyle](https://pycodestyle.pycqa.org/en/latest/) to make sure that your code follows the PEP8 standard.

### Adding License Headers
The content in this repository was initially created by engineers at
Cisco Systems, Inc. which holds the copyright for all files and licenses them for
use under the BSD 3-Clause License. Please be sure to add our [LICENSEHEADER](LICENSEHEADER)
to any new files you add.

Use https://github.com/google/addlicense to automatically add license headers.
This tool is open sourced with Apache 2.0 license.
```
docker run --rm -it -v ${PWD}:/src ghcr.io/google/addlicense -f LICENSEHEADER -ignore **/swagger.yaml -ignore **/models.py .
```
This tool can't remove or update license headers, so removing
license headers would need a separate script or manual process.
