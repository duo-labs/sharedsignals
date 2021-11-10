#!/usr/bin/env python3
# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.
#

import argparse
import sys
import logging
import socket
import time
import requests
import threading
import os
from pathlib import Path
from typing import Any
import jwt
from jwcrypto.jwk import JWKSet
from http.server import HTTPServer, BaseHTTPRequestHandler


class TransmitterInfo:
    """A class that holds the transmitter endpoint information"""

    def __init__(self, info: dict[str, Any], unsafe: bool, hostname: str):
        # FIXME get issuer information
        self.unsafe = unsafe
        self.add_subject_endpoint = info['add_subject_endpoint']
        self.configuration_endpoint = info['configuration_endpoint']
        self.jwks_uri = info['jwks_uri']
        self.remove_subject_endpoint = info['remove_subject_endpoint']
        self.status_endpoint = info['status_endpoint']
        self.verification_endpoint = info['verification_endpoint']
        self.supported_methods = info['delivery_methods_supported']
        self.jwks = JWKSet.from_json(requests.get(
            self.jwks_uri, verify=not unsafe).text)
        self.audience = "http://example_receiver"
        reg = requests.post(f"https://{hostname}/register",
                            verify=not unsafe,
                            json={"audience": self.audience})
        self.known_client_id = reg.json()["token"]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"TransmitterInfo(add_subject_endpoint={self.add_subject_endpoint}, configuration_endpoint={self.configuration_endpoint}, jwks_uri={self.jwks_uri}, remove_subject_endpoint={self.remove_subject_endpoint}, status_endpoint={self.status_endpoint}, verification_endpoint={self.verification_endpoint}, supported_methods={self.supported_methods}, unsafe={self.unsafe}, jwks={self.jwks})"

    def supports_push(self) -> bool:
        """Does the endpoint support push methods?"""
        for v in self.supported_methods:
            if v == 'https://schemas.openid.net/secevent/risc/delivery-method/push':
                return True
        return False

    def supports_push(self) -> bool:
        """Does the endpoint support poll methods?"""
        for v in self.supported_methods:
            if v == 'https://schemas.openid.net/secevent/risc/delivery-method/poll':
                return True
        return False

    def build_auth(self) -> dict[str, str]:
        """Build the 'Authorization' line for the HTTP header"""

        return {
            'Authorization': f"Bearer {self.known_client_id}",
        }


def make_poll_request(info: TransmitterInfo, hostname: str):
    """Make a poll request on the demo transmitter... not called, but 
    good for example purposes"""

    poll_data = requests.post(
        url=info.configuration_endpoint,
        verify=not info.unsafe,
        json={
            'delivery': {
                'method': 'https://schemas.openid.net/secevent/risc/delivery-method/poll',
                'endpoint_url': None
            },
            'events_requested': [

                'https://schemas.openid.net/secevent/risc/event-type/credential-compromise',
            ]
        },
        headers=info.build_auth()
    )

    poll_body = poll_data.json()

    verification_response = requests.post(
        url=info.verification_endpoint,
        verify=not info.unsafe,
        json={
            'state': 'VGhpcyBpcyBhbiBleG'
        },
        headers=info.build_auth()
    )

    add_subject_response = requests.post(
        url=info.add_subject_endpoint,
        verify=not info.unsafe,
        json={
            'subject': {
                'format': 'email',
                'email': '*'
            }
        },
        headers=info.build_auth())

    # Do a polling request before registering for push events
    polling_response = requests.post(
        url=poll_body['delivery']['endpoint_url'],
        verify=not info.unsafe,
        json={
            "maxEvents": 1,
            "returnImmediately": True
        },
        headers=info.build_auth()
    )
    events = polling_response.json()


def make_requests(info: TransmitterInfo, hostname: str):
    """Make requests on the demo transmitter"""
    # Pause to allow the http server that receives push commands to start
    time.sleep(1)

    if not info.supports_push():
        logging.warning("The Transmitter does not support push, exiting")
        sys.exit(1)

    # Set up push requests
    push = requests.post(
        url=info.configuration_endpoint,
        verify=not info.unsafe,
        json={
            'delivery': {
                'method': 'https://schemas.openid.net/secevent/risc/delivery-method/push',
                'endpoint_url': f"http://{hostname}:5003"
            },
            'events_requested': [
                'https://schemas.openid.net/secevent/risc/event-type/credential-compromise',
            ]
        },
        headers=info.build_auth()
    )

    add_subject_response = requests.post(
        url=info.add_subject_endpoint,
        verify=not info.unsafe,
        json={
            'subject': {
                'format': 'email',
                'email': '*'
            }
        },
        headers=info.build_auth())

    while True:
        verification_response = requests.post(
            url=info.verification_endpoint,
            verify=not info.unsafe,
            json={
                'state': 'VGhpcyBpcyBhbiBleG'
            },
            headers=info.build_auth()
        )
        time.sleep(2)


def main():
    time.sleep(5)  # Wait for transmitter to start
    # FIXME do in docker compose rather than here

    # Get this instance's hostname
    hostname = socket.gethostname()

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-x", "--xmit", help="Set the hostname of the Shared Signals Transmitter")
    parser.add_argument("--unsafe", action="store_true",
                        help="connect to server ignoring TLS certificate")
    args = parser.parse_args()

    # If the name of the transmitter is not specified, assume we're in `docker compose`
    # and the demo transmitter is named "transmitter"
    args.xmit = args.xmit or "transmitter"

    # Use env-vars or CLI for the "unsafe" flag
    args.unsafe = args.unsafe or (os.environ["UNSAFE_TLS"] == "True")

    # Get the transmitter's endpoints
    r = requests.get(
        f"https://{args.xmit}/.well-known/sse-configuration", verify=not args.unsafe)

    info = TransmitterInfo(r.json(), args.unsafe, args.xmit)

    # Define a class that handles the "push requests"
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            kid = jwt.get_unverified_header(body)["kid"]
            jwk = info.jwks.get_key(kid)
            key = jwt.PyJWK(jwk).key
            decoded = jwt.decode(
                jwt=body,
                key=key,
                algorithms=["ES256"],
                audience=info.audience
            )
            logging.warning(f"Got message: {decoded}")
            self.send_response(202)
            self.end_headers()

    server_address = ("0.0.0.0", 5003)
    httpd = HTTPServer(server_address, Handler)

    t = threading.Thread(target=make_requests, args=[
                         info, hostname])
    t.start()

    httpd.serve_forever()


if __name__ == '__main__':
    main()
