# Example Receiver
In order to test out the PUSH delivery method of the SSE spec, we have created a
recevier service that will spin up, configure the stream, and then host an
endpoint where the transmitter can push events. Those events will be logged to
std out. This service also has a `/request_verification` endpoint which, when
called (via the browser or other method), will cause the receiver to request a
Verification Event from the transmitter. This allows you to force the tranmitter
to generate an event to demonstrate the PUSH capability.

## Requirements
Python 3.9+

## Run with Docker Compose

From the `examples` directory:
```
docker-compose up
```
will build an image named `transmitter_1` as well as an image named `receiver_1`
and run them both with development settings (hot-reloading).

## Run with Docker

To run the server on a Docker container, please execute the following from the `examples/transmitter` directory:

```bash
# building the image
docker build -f Dockerfile -t transmitter .

# starting up a container
docker run -p 443:443 -v "${PWD}":/usr/src/app transmitter
```

You can then run the receiver from the `examples/receiver` directory:
```bash
# building the image
docker build -f Dockerfile -t receiver .

# starting up a container
docker run -p 5003:5003 -v "${PWD}":/usr/src/app receiver
```

Note that this runs both transmitter and receiver without hot-reloading.


## Environment variables
There are a few environment variables you can set to control how the transmitter
works:

- `FLASK_ENV=development` This will cause the flask server to hot-reload if you change
any code while it is running.
- `CONFIG_FILENAME=config.cfg` This allows you to specify the config filename that
contains information about the transmitter to attach to, the subjects to listen for, etc.

## Usage
When run, the receiver should output messages on stdout describing any events it
receives. In order to trigger an event, you can visit
[http://localhost:5003/request_verification](http://localhost:5003/request_verification).
Your browser will show a message that a request for verification has been sent,
and you should eventually see the event appear on stdout.
