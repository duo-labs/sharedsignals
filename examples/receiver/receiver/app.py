# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

import asyncio
import socket
import sys
import logging
import time
import requests
import threading
import os
import json
import urllib
from pathlib import Path
from typing import Any
from flask import Flask, request
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


def create_app(config_filename: str = "config.cfg"):
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
    app.config.from_pyfile(config_filename)
    verify = app.config.get("VERIFY", True)

    # Wait for transmitter to be available
    transmitter_url = app.config["TRANSMITTER_URL"]
    asyncio.run(wait_until_available(urllib.parse.urlparse(transmitter_url).netloc, 443))

    bearer = app.config.get('BEARER')
    if not bearer:
        # Register stream
        reg = requests.post(f"{transmitter_url}/register",
                            verify=verify,
                            json={"audience": app.config["AUDIENCE"]})
        bearer = reg.json()["token"]

    client = TransmitterClient(transmitter_url, app.config["AUDIENCE"], bearer, verify)
    client.get_endpoints()
    client.get_jwks()
    stream_config = client.configure_stream(f"{app.config['RECEIVER_URL']}/event")
    for subject in app.config["SUBJECTS"]:
        client.add_subject(subject)

    @app.route('/event', methods=['POST'])
    def receive_event():
        body = request.get_data()
        event = client.decode_body(body)
        app.logger.info(json.dumps(event, indent=2))
        return "", 202

    @app.route('/request_verification')
    def request_verification():
        client.request_verification().raise_for_status()
        return "Submitted request for verification event"

    return app
