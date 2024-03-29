# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

import uuid
from typing import Union, Any
import requests
import jwt
from jwcrypto.jwk import JWKSet


class TransmitterClient:
    """A class that holds information for interacting with the transmitter"""

    def __init__(self, transmitter_hostname: str, audience: str, bearer: str, verify: bool = True):
        self.transmitter_hostname = transmitter_hostname
        self.audience = audience
        self.auth = {"Authorization": f"Bearer {bearer}"}
        self.verify = verify

    def get_endpoints(self):
        ssf_config_response = requests.get(
            f"{self.transmitter_hostname}/.well-known/sse-configuration", verify=self.verify)
        ssf_config_response.raise_for_status()
        self.ssf_config = ssf_config_response.json()

    def get_jwks(self):
        jwks_response = requests.get(self.ssf_config["jwks_uri"], verify=self.verify)
        jwks_response.raise_for_status()
        self.jwks = JWKSet.from_json(jwks_response.text)

    def decode_body(self, body: Union[str, bytes]):
        kid = jwt.get_unverified_header(body)["kid"]
        jwk = self.jwks.get_key(kid)
        key = jwt.PyJWK(jwk).key
        return jwt.decode(
            jwt=body,
            key=key,
            algorithms=[jwk["alg"]],
            issuer=self.ssf_config["issuer"],
            audience=self.audience,
        )

    def configure_stream(self, endpoint_url: str):
        """ Configure stream and return the current config """
        config_response = requests.post(
            url=self.ssf_config["configuration_endpoint"],
            verify=self.verify,
            json={
                'delivery': {
                    'method': 'https://schemas.openid.net/secevent/risc/delivery-method/push',
                    'endpoint_url': endpoint_url,
                },
                'events_requested': [
                    'https://schemas.openid.net/secevent/risc/event-type/credential-compromise',
                ]
            },
            headers=self.auth,
        )
        config_response.raise_for_status()
        self.stream_config = config_response.json()

    def add_subject(self, subject: dict[str: Any]):
        return requests.post(
            url=self.ssf_config["add_subject_endpoint"],
            verify=self.verify,
            json={'subject': subject},
            headers=self.auth
        )

    def request_verification(self):
        """ Request a single verification event """
        return requests.post(
            url=self.ssf_config["verification_endpoint"],
            verify=self.verify,
            json={'state': uuid.uuid4().hex},
            headers=self.auth,
        )
