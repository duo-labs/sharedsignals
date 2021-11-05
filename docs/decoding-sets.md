# Decoding SETs with ES256 Algorithm

SETs can be encoded with various different algorithms. We recommend encoding
with the ES256 algorithm for maximum security.

## Retrieving the JWKS
To decode SETs from a transmitter, we need the transmitter's JWKS (JSON Web Key Set):
```py
sse_config_response = requests.get(
    'https://transmitter.most-secure.com/.well-known/sse-configuration')
sse_config = sse_config_response.json()
jwks_uri = sse_config['jwks_uri']  # for example, https://transmitter.most-secure.com/jwks.json
jwks = requests.get(jwks_uri).json()
```

An example of what `jwks` might look like:
```py
jwks = {
  "keys": [
    {
      "kty": "EC",
      "crv": "P-256",
      "alg": "ES256",
      "kid": "transmitter-ES256-001",
      "x": "Js-Hzhls17UL1JI2EL0AB6Ta2B282me2niBGc0s1-Lo",
      "y": "PCsSWYCixwZgEyYKbGDFpzaooP6_Z-4CEfV62cbNBQw"
    }
  ]
 }
```

This describes the public portion of the key that the transmitter uses to encode SETs.
It might be confusing to the human eye, but the PyJWT library will have no problem
understanding how to use it!

## Decoding
Now let's say we received a response from our transmitter's polling endpoint that looked like this:
```py
events = {
  "sets": {
    # The key is the JTI of the event -- a unique identifier
    # The value is an encoded event body
    "9e668e802d0311eca8830242ac120005": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI5ZTY2OGU4MDJkMDMxMWVjYTg4MzAyNDJhYzEyMDAwNSIsImlhdCI6MTYzNDIyNTQxMCwiaXNzIjoiaHR0cHM6Ly90cmFuc21pdHRlci5tb3N0LXNlY3VyZS5jb20vIiwiYXVkIjoiaHR0cHM6Ly9wb3B1bGFyLWFwcC5jb20iLCJldmVudHMiOnsiaHR0cHM6Ly9zY2hlbWFzLm9wZW5pZC5uZXQvc2VjZXZlbnQvc3NlL2V2ZW50LXR5cGUvdmVyaWZpY2F0aW9uIjp7InN0YXRlIjoiVkdocGN5QnBjeUJoYmlCbGVHIn19fQ.7FsbAXOXJgwkwPLNIlnff1bgshWBLHq9-m8VGc6KjWQ"
  },
  "moreAvailable": false
}
```

We have the JWKS data and an encoded event to work with, now let's use PyJWT to decode it:
```py
import jwt
encoded_set = next(iter(events['sets'].values()))

# get the key id from the header of the JWT
kid = jwt.get_unverified_header(encoded_set)["kid"]

# and use it to select the right JWK
jwk = [jwk for jwk in jwks["keys"] if jwk["kid"] == kid][0]
key = jwt.PyJWK(jwk).key

# In order to decode the set you must prove that you know its issuer and audience.
# This information is established upon creating a stream and can be retrieved
# by making an authenticated request to the stream configuration endpoint:
stream_config_endpoint = sse_config['stream_config_endpoint']
stream_config = requests.get(
    stream_config_endpoint,
    headers={'Authorization': 'Bearer 49e5e7785e4e4f688aa49e2585970370'},
).json()

decoded_set = jwt.decode(
    jwt=encoded_set,
    key=key,
    algorithms=[jwk["alg"]],
    issuer=stream_config["iss"],
    audience=stream_config["aud"],
)
```

Success! Here's the decoded event:
```json5
{
  "jti": "bd28254a35a511ecbca20242ac1c0002",
  "iat": 1634225410,
  "iss": "https://most-secure.com/",
  "aud": "https://popular-app.com",
  "events": {
    "https://schemas.openid.net/secevent/sse/event-type/verification": {
      "state": "VGhpcyBpcyBhbiBleG"
    }
  }
}
```
