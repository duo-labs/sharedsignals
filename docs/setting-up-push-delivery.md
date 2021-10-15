# Push Delivery
Push configuration is an alternative to poll delivery, in which the transmitter
sends events one-at-a-time to an endpoint configured by the receiver. Push
configuration is ideal for event receivers who want to ensure they
receive events in real time, without needing to poll continuously.


## Receiver Example
A python example for a push event receiver:

```py
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import jwt

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        decoded = jwt.decode(body, key="mysymmetrickey", algorithms=["HS256"], audience="example_receiver")
        print(json.dumps(decoded, indent=2))
        self.send_response(202)
        self.end_headers()

if __name__ == "__main__":
    server_address = ("localhost", 8080)
    httpd = HTTPServer(server_address, Handler)
    print(f"Starting on {server_address}")
    httpd.serve_forever()
```

Running this python file will start the receiver listening for events. This
example receiver simply prints the decoded SET and acknowledges it by returning
HTTP status code 202.

## Transmitter Example
A python example for pushing a single event to the receiver:

```py
import requests
import jwt

encoded_jwt = jwt.encode({
    "iss": "https://idp.example.com/",
    "jti": "756E69717565206964656E746966696572",
    "iat": 1508184845,
    "aud": "example_receiver",
    "events": {
        "https://schemas.openid.net/secevent/risc/event-type/account-disabled": {
            "subject": {
                "subject_type": "iss-sub",
                "iss": "https://idp.example.com/",
                "sub": "7375626A656374"
            },
            "reason": "hijacking"
        }
    }
}, key="mysymmetrickey", algorithm="HS256")

requests.post("http://localhost:8080", data=encoded_jwt, headers={
        "content-type": "application/secevent+jwt",
        "accept": "application/json"
    }
)
```

To avoid the challenge of sharing an asymmetric key pair between the two
examples, this example transmitter encodes SETS using the symmetric key HS256
algorithm. For enhanced protection, an asymmetric key algorithm such as ES256
should be used, and the transmitter's public key should be shared with the
receiver out-of-band.


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