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

    def __init__(self, info: dict[str, Any]):
        self.add_subject_endpoint = info['add_subject_endpoint']
        self.configuration_endpoint = info['configuration_endpoint']
        self.jwks_uri = info['jwks_uri']
        self.remove_subject_endpoint = info['remove_subject_endpoint']
        self.status_endpoint = info['status_endpoint']
        self.verification_endpoint = info['verification_endpoint']
        self.supported_methods = info['delivery_methods_supported']

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"TransmitterInfo(add_subject_endpoint={self.add_subject_endpoint}, configuration_endpoint={self.configuration_endpoint}, jwks_uri={self.jwks_uri}, remove_subject_endpoint={self.remove_subject_endpoint}, status_endpoint={self.status_endpoint}, verification_endpoint={self.verification_endpoint})"

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


def make_requests(info: TransmitterInfo, hostname: str, unsafe: bool):
    time.sleep(1)  # Pause to allow the http server to start

    if not info.supports_push():
        print("The Transmitter does not support push, exiting")
        sys.exit(1)

    jwks_json = requests.get(info.jwks_uri, verify=not unsafe).text

    jwks = JWKSet.from_json(jwks_json)

    events = requests.get(info.status_endpoint, verify=not unsafe, headers={
        # FIXME compute bearer token
        'Authorization': 'Bearer 49e5e7785e4e4f688aa49e2585970370',
    })

    logging.warning(f"status {events.text} code {events}")

    poll_data = requests.post(
        url=info.configuration_endpoint,
        verify=not unsafe,
        json={
            'delivery': {
                'method': 'https://schemas.openid.net/secevent/risc/delivery-method/poll',
                'endpoint_url': None
            },
            'events_requested': [
                'https://schemas.openid.net/secevent/risc/event-type/credential-compromise',
            ]
        },
        headers={
            'Authorization': 'Bearer 49e5e7785e4e4f688aa49e2585970370',
        }
    )

    logging.warning(
        f"poll info {poll_data} text {poll_data}")

    push = requests.post(
        url=info.configuration_endpoint,
        verify=not unsafe,
        json={
            'delivery': {
                'method': 'https://schemas.openid.net/secevent/risc/delivery-method/push',
                'endpoint_url': f"http://{hostname}:5003"
            },
            'events_requested': [
                'https://schemas.openid.net/secevent/risc/event-type/credential-compromise',
            ]
        },
        headers={
            'Authorization': 'Bearer 49e5e7785e4e4f688aa49e2585970370',
        }
    )

    logging.warning(f"register for push {push} body {push.text}")

    while True:
        time.sleep(2)


def load_jwks() -> JWKSet:
    """Load the keys from the shared volume"""
    jwks_path = Path(os.environ["JWKS_PATH"])
    with open(jwks_path, "r") as fin:
        all_of_it = fin.read()
        ret = JWKSet.from_json(all_of_it)
        return ret


def main():
    time.sleep(5)  # Wait for transmitter

    hostname = socket.gethostname()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-x", "--xmit", help="Set the hostname of the Shared Signals Transmitter")
    parser.add_argument("--unsafe", action="store_true",
                        help="connect to server ignoring TLS certificate")
    args = parser.parse_args()

    args.xmit = args.xmit or "transmitter"

    args.unsafe = args.unsafe or (os.environ["UNSAFE_TLS"] == "True")

    if args.xmit is None:
        print("You must supply the --xmit parameter with the host of the SSE transmitter")
        sys.exit(1)

    keys = load_jwks()

    logging.warn(f"Loaded keys {keys}")

    r = requests.get(
        f"https://{args.xmit}/.well-known/sse-configuration", verify=not args.unsafe)

    info = TransmitterInfo(r.json())

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            kid = jwt.get_unverified_header(body)["kid"]
            jwk = jwks.get_key(kid)
            key = jwt.PyJWK(jwk).key
            decoded = jwt.decode(
                jwt=body,
                key=key,
                algorithms=["ES256"],
                issuer="example_push_transmitter",
                audience="example_push_receiver",
            )
            logging.warning(json.dumps(decoded, indent=2))
            self.send_response(202)
            self.end_headers()

    server_address = ("0.0.0.0", 5003)
    httpd = HTTPServer(server_address, Handler)

    t = threading.Thread(target=make_requests, args=[
                         info, hostname, args.unsafe])
    t.start()

    httpd.serve_forever()


if __name__ == '__main__':
    main()
