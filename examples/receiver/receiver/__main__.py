#!/usr/bin/env python3
# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.
#

import asyncio
import sys
import logging
import socket
import time
import requests
import threading
import os
import json
from pathlib import Path
from typing import Any
from flask import Flask, request
import jwt
from jwcrypto.jwk import JWKSet
from http.server import HTTPServer, BaseHTTPRequestHandler
from logging.config import dictConfig
from .client import TransmitterClient


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


async def main():
    # Define a flask app that handles the push requests
    dictConfig({
        "version": 1,
        "formatters": {"default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        }},
        "handlers": {"wsgi": {
            "class": "logging.StreamHandler",
            "stream": "ext://flask.logging.wsgi_errors_stream",
            "formatter": "default"
        }},
        "root": {
            "level": "INFO",
            "handlers": ["wsgi"]
        }
    })

    app = Flask(__name__)
    app.config.from_pyfile("config.cfg")
    app.logger.info(app.config)
    verify = app.config.get("VERIFY", True)

    # Wait for transmitter to be available
    await wait_until_available(app.config["TRANSMITTER_HOSTNAME"], 443)

    bearer = app.config.get('BEARER')
    if not bearer:
        # Register stream
        reg = requests.post(f"https://{app.config['TRANSMITTER_HOSTNAME']}/register",
                            verify=verify,
                            json={"audience": app.config["AUDIENCE"]})
        bearer = reg.json()["token"]

    # Get the transmitter's endpoints and setup jwks
    sse_config_response = requests.get(
        f"https://{app.config['TRANSMITTER_HOSTNAME']}/.well-known/sse-configuration", verify=verify)
    sse_config = sse_config_response.json()
    jwks_json = requests.get(sse_config["jwks_uri"], verify=verify).text
    jwks = JWKSet.from_json(jwks_json)

    client = TransmitterClient(sse_config, verify, app.config["AUDIENCE"], bearer)
    stream_config = client.configure_stream()

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
            issuer=stream_config["iss"],
            audience=app.config["AUDIENCE"],
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
