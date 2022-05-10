# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

import asyncio
from asyncio import events
import socket
import time
import json
import threading
from logging import Logger
from logging.config import dictConfig

import urllib
import requests
from flask import Flask, request

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


def poll_events_continuously(client: TransmitterClient, poll_url: str, logger: Logger):
    while True:
        more_avaliable = True
        while more_avaliable:
            rsp = client.poll_events(poll_url)
            for event in rsp['sets'].values():
                logger.info(json.dumps(event, indent=2))
            more_avaliable = rsp['moreAvailable']

        time.sleep(5)


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
    transmitter_url = "https://" + app.config["TRANSMITTER_HOST"]
    asyncio.run(wait_until_available(app.config["TRANSMITTER_HOST"], 443))

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

    client.configure_stream(app.config['STREAM_CONFIG'])

    for subject in app.config["SUBJECTS"]:
        client.add_subject(subject)

    if client.stream_config['delivery']['method'].endswith('poll'):
        poll_url = client.stream_config['delivery']['endpoint_url']
        # Need to replace domain name in endpoint_url because there are different endpoint names 
        # for reciever and shared_signals_guide
        poll_url_parsed = urllib.parse.urlparse(poll_url)
        poll_url_parsed = poll_url_parsed._replace(netloc=app.config["TRANSMITTER_HOST"])
        poll_url = poll_url_parsed.geturl()

        thread = threading.Thread(target=poll_events_continuously, 
                                  args=(client, poll_url, app.logger))
        thread.start()

    @app.route('/event', methods=['POST'])
    def receive_event():
        body = request.get_data()
        event = client.decode_event(body)
        app.logger.info(json.dumps(event, indent=2))
        return "", 202

    @app.route('/request_verification')
    def request_verification():
        client.request_verification().raise_for_status()
        return "Submitted request for verification event"

    return app
