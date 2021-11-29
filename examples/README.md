# Examples
Code meant to help explain how the Shared Signals and Events (SSE) Framework is supposed
to work. We do not recommend using this code in production, although you are welcome
to start from this code and build a more production-ready system.

## Running the examples
To run the `transmitter` and `receiver` examples, please run `docker compose up`
from this directory.

## Transmitter
A web server that hosts the Stream Configuration endpoints, as well as a place
to poll for events. Will also create a `/ui` page that shows Swagger documentation
of the OpenAPI spec described in [transmitter_spec](../transmitter_spec/openapi.yaml).

We have added a `/register` endpoint to this service, which is not part of the
Shared Signals spec, because we needed an easy way to create streams and provide
bearer tokens. As the SSE spec continues to evolve, this endpoint may become
unnecessary.

## Receiver
In order to test out the PUSH delivery method of the SSE spec, we have created a
receiver service that will spin up, configure the stream, and then host an
endpoint where the transmitter can push events. Those events will be logged to
std out. This service also has a `/request_verification` endpoint which, when
called (via the browser or other method), will cause the receiver to request a
Verification Event from the transmitter. This allows you to force the transmitter
to generate an event to demonstrate the PUSH capability.

## shared_signals_guide
This collection of scripts and JSON walks through the examples shown on the
[https://sharedsignals.guide](https://sharedsignals.guide) website. It assumes
you already have the example transmitter up and running.
