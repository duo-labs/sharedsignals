# Push Delivery
Push configuration is an alternative to poll delivery, in which the transmitter
sends events one-at-a-time to an endpoint configured by the receiver. Push
configuration is ideal for event receivers who want to ensure they
receive events in real time, without needing to poll continuously.


## Receiver Example
A python example for a simple push event receiver:

```py
import json
from flask import Flask, request
import requests
import jwt
from jwcrypto.jwk import JWKSet


def main():
    # Get jwks information from the transmitter so we can decode events
    ssf_config_response = requests.get(
        "https://transmitter.most-secure.com/.well-known/sse-configuration"
    )
    ssf_config = ssf_config_response.json()
    jwks_json = requests.get(ssf_config['jwks_uri']).text
    jwks = JWKSet.from_json(jwks_json)

    app = Flask(__name__)

    @app.route('/event', methods=['POST'])
    def receive_event():
        data = request.get_data()
        kid = jwt.get_unverified_header(data)["kid"]
        jwk = jwks.get_key(kid)
        key = jwt.PyJWK(jwk).key
        decoded = jwt.decode(
            jwt=data,
            key=key,
            algorithms=["ES256"],
            issuer="example_push_transmitter",
            audience="example_push_receiver",
        )
        print(json.dumps(decoded, indent=2))
        return "", 202

    app.run("localhost", 8080)


if __name__ == "__main__":
    main()
```

As seen here, the main thing that a push receiver needs to set up is an endpoint
that can receive and decode events in POST message bodies.
A transmitter could then push an event to this receiver with an http call:

```py
requests.post("http://localhost:8080", data=encoded_jwt, headers={
        "content-type": "application/secevent+jwt",
        "accept": "application/json"
    }
)
```

In a full implementation, the transmitter must share its `jwks.json` file with the receiver
and encode each JWT. This process is omitted from this example -- see
[the full transmitter](https://github.com/duo-labs/sharedsignals/tree/main/examples/transmitter)
example in this repository to learn how SETs can be encoded using the ES256 algorithm


## Errors
In the case of an error, the receiver should instead respond with an HTTP 400 failure code response with a json body describing the error:

```json
{
  "err": "invalid_key",
  "description": "Key ID 12345 has been revoked"
}
```

- `err`: An IANA Security Event Token Error Code that identifies the error
- `description`: A human-readable string that provides additional diagnostic information.
The language used should match the language requested by the transmitter in its Accept-Language header

This notifies the transmitter that something went wrong with the event,
and it should do something to fix the event before attempting to resend it.

### IANA Security Event Token Error Codes

Note that for simplicity's sake, the example receiver shown above does not handle error scenarios.
In a production setting, the event receiver should include code capable of analyzing an error scenario
and returning the appropriate
[IANA Security Event Token Error Code](https://www.iana.org/assignments/secevent/secevent.xhtml)
back to the transmitter:

| Error Code | Description |
| ---------- | ----------- |
| invalid_request |  The request body cannot be parsed as a SET or the Event Payload within the SET does not conform to the event's definition |
| invalid_key | One or more keys used to encrypt or sign the SET is invalid or otherwise unacceptable to the SET Recipient (expired, revoked, failed certificate validation, etc.) |
| invalid_issuer | The SET Issuer is invalid for the SET Recipient |
| invalid_audience | The SET Audience does not correspond to the SET Recipient |
| authentication_failed | The SET Recipient could not authenticate the SET Transmitter |
| access_denied | The SET Transmitter is not authorized to transmit the SET to the SET Recipient |
