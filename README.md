# py-openid-sse

Python tools for working with OpenID's
[Shared Signals and Events Framework](https://openid.net/specs/openid-sse-framework-1_0.html)
as well as the [CAEP standard](https://openid.net/specs/openid-caep-specification-1_0-02.html).

## Installing
Download this code and run `pip install .` from the root directory.

## Models
For easy creation and parsing of CAEP and RISC events, you can use the classes
available at the root of the `openid_sse`

For instance, to parse the [SessionRevoked example](https://openid.net/specs/openid-caep-specification-1_0-02.html#rfc.section.3.1.2)
provided in the CAEP standard, you would do as follows

```python
from openid_sse import SessionRevoked

data = {
    "iss": "https://idp.example.com/123456789/",
    "jti": "24c63fb56e5a2d77a6b512616ca9fa24",
    "iat": 1615305159,
    "aud": "https://sp.example.com/caep",
    "events": {
        "https://schemas.openid.net/secevent/caep/event-type/session-revoked": {
            "subject": {
                "format": "opaque",
                "id": "dMTlD|1600802906337.16|16008.16"
            },
            "event_timestamp": 1615304991643
        }
    }
}

session_revoked_jwt = SessionRevoked(**data)
```

## Contributing
As a developer, you will want to create a virtual environment and install the
dev requirements via `pip install -r dev-requirements.txt`. This will install
`openid_sse` as an editable package in your virtualenv.

You can test the code by running `pytest` from the root directory.
And you can check the static typing by running `mypy` from the root directory.
