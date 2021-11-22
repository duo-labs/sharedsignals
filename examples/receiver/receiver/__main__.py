#!/usr/bin/env python3
# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.
#

import asyncio
import argparse
import sys
import logging
import socket
import time
import requests
import threading
import os
import uuid
import json
from pathlib import Path
from typing import Any
from flask import Flask, request
import jwt
from jwcrypto.jwk import JWKSet
from http.server import HTTPServer, BaseHTTPRequestHandler
from logging.config import dictConfig


# borrowed + adapted from https://github.com/clarketm/wait-for-it
async def wait_until_available(host, port):
    while True:
        try:
            _reader, writer = await asyncio.open_connection(host, port)
            writer.close()
            await writer.wait_closed()
            break
        except (socket.gaierror, ConnectionError, OSError, TypeError):
            pass
        await asyncio.sleep(1)


class TransmitterClient:
    """A class that holds information for interacting with the transmitter"""

    def __init__(self, sse_config: dict[str, str], verify: bool, audience: str, auth: str):
        # FIXME get issuer information
        self.sse_config = sse_config
        self.verify = verify
        self.audience = audience
        self.auth = auth

    def configure_stream(self):
        config_response = requests.post(
            url=self.sse_config["configuration_endpoint"],
            verify=self.verify,
            json={
                'delivery': {
                    'method': 'https://schemas.openid.net/secevent/risc/delivery-method/push',
                    'endpoint_url': "http://receiver:5003/event"
                },
                'events_requested': [
                    'https://schemas.openid.net/secevent/risc/event-type/credential-compromise',
                ]
            },
            headers=self.auth,
        )
        config_response.raise_for_status()

        add_subject_response = requests.post(
            url=self.sse_config["add_subject_endpoint"],
            verify=self.verify,
            json={
                'subject': {
                    'format': 'email',
                    'email': '*'
                }
            },
            headers=self.auth
        )
        return config_response.json()

    def request_verification(self):
        """Make requests on the demo transmitter"""
        return requests.post(
            url=self.sse_config["verification_endpoint"],
            verify=self.verify,
            json={'state': uuid.uuid4().hex},
            headers=self.auth,
        )


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-x", "--xmit", default="transmitter",
        help="Set the hostname of the Shared Signals Transmitter",
    )
    parser.add_argument(
        "--unsafe", action="store_true",
        default=os.environ.get("UNSAFE_TLS", True),
        help="connect to server ignoring TLS certificate",
    )
    args = parser.parse_args()

    # Wait for transmitter to be available
    await wait_until_available(args.xmit, 443)

    # Register stream
    audience = "http://example_receiver"
    reg = requests.post(f"https://{args.xmit}/register",
                        verify=not args.unsafe,
                        json={"audience": audience})
    auth = {'Authorization': f"Bearer {reg.json()['token']}"}

    # Get the transmitter's endpoints and setup jwks
    sse_config_response = requests.get(
        f"https://{args.xmit}/.well-known/sse-configuration", verify=not args.unsafe)
    sse_config = sse_config_response.json()
    jwks_json = requests.get(sse_config['jwks_uri'], verify=not args.unsafe).text
    jwks = JWKSet.from_json(jwks_json)

    client = TransmitterClient(sse_config, not args.unsafe, audience, auth)
    config = client.configure_stream()

    # Define a flask app that handles the push requests
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })

    app = Flask(__name__)

    @app.route('/event', methods=['POST'])
    def receive_event():
        body = request.get_data()
        kid = jwt.get_unverified_header(body)["kid"]
        jwk = jwks.get_key(kid)
        key = jwt.PyJWK(jwk).key
        decoded = jwt.decode(
            jwt=body,
            key=key,
            algorithms=["ES256"],
            issuer=config["iss"],
            audience=audience,
        )
        app.logger.info(json.dumps(decoded, indent=2))
        return "", 202

    @app.route('/request_verification')
    def request_verification():
        client.request_verification().raise_for_status()
        return "Submitted request for verification event"

    app.run("0.0.0.0", 5003)


if __name__ == '__main__':
    asyncio.run(main())
