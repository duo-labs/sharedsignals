# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

import json
import argparse

import jwt
import requests

from utils import no_ssl_verification, patch_hosts


DEFAULT_TRANSMITTER = 'transmitter.most-secure.com'


def main(host):
    # Step 1: Request the transmitter config from /.well-known/sse-configuration
    ssf_config_response = requests.get(
        url=f'https://{host}/.well-known/sse-configuration',
    )
    ssf_config = ssf_config_response.json()
    print('example_transmitter_config.json:', json.dumps(ssf_config, indent=2))

    # Step 2: Modify the stream config using the configuration_endpoint from step 1
    stream_config_response = requests.post(
        url=ssf_config['configuration_endpoint'],
        json={
            'delivery': {
                'method': 'https://schemas.openid.net/secevent/risc/delivery-method/poll',
                'endpoint_url': None
            },
            'events_requested': [
                'https://schemas.openid.net/secevent/risc/event-type/credential-compromise'
            ],
            'format': 'email'
        },
        headers={
            'Authorization': 'Bearer 49e5e7785e4e4f688aa49e2585970370'
        }
    )
    stream_config = stream_config_response.json()
    print("example_stream_config.json:", json.dumps(stream_config, indent=2))

    # Step 3: Add a subject to the stream using the add_subject_endpoint from step 1
    add_subject_response = requests.post(
        url=ssf_config['add_subject_endpoint'],
        json={
            'subject': {
                'format': 'email',
                'email': 'reginold@popular-app.com'
            }
        },
        headers = {
            'Authorization': 'Bearer 49e5e7785e4e4f688aa49e2585970370'
        }
    )
    print("add_subject_response:", add_subject_response.status_code, add_subject_response.reason)

    # Step 4: Request a verification SET using the verification_endpoint from step 1
    verification_response = requests.post(
        url=ssf_config['verification_endpoint'],
        json={
            'state': 'VGhpcyBpcyBhbiBleG'
        },
        headers={
            'Authorization': 'Bearer 49e5e7785e4e4f688aa49e2585970370'
        }
    )
    print("verification_response:", verification_response.status_code, verification_response.reason)

    # Step 5: Get the event from the Transmitter's polling endpoint
    polling_response = requests.post(
        url=stream_config['delivery']['endpoint_url'],
        json={
            "maxEvents": 1,
            "returnImmediately": True
        },
        headers={
            'Authorization': 'Bearer 49e5e7785e4e4f688aa49e2585970370'
        }
    )
    events = polling_response.json()
    print("example_polling_response.json:", json.dumps(events, indent=2))

    # Step 6: Get the JSON Web Key Set (JWKS) for decoding the event
    jwks_uri = ssf_config['jwks_uri']
    jwks = requests.get(jwks_uri).json()
    print("example_jwks.json:", json.dumps(jwks, indent=2))

    # Step 7: Decode the SET with pyjwt
    encoded_set = next(iter(events['sets'].values()))

    # get the key id from the header of the JWT
    kid = jwt.get_unverified_header(encoded_set)["kid"]

    # and use it to select the right JWK
    jwk = [jwk for jwk in jwks["keys"] if jwk["kid"] == kid][0]
    key = jwt.PyJWK(jwk).key

    decoded_set = jwt.decode(
        jwt=encoded_set,
        key=key,
        algorithms=[jwk["alg"]],
        issuer=stream_config["iss"],
        audience=stream_config["aud"]
    )
    print("example_decoded_set.json", json.dumps(decoded_set, indent=2))

    # Step 7: Acknowledge receipt of the event
    jtis_to_ack = list(events['sets'].keys())
    ack_response = requests.post(
        url=stream_config['delivery']['endpoint_url'],
        json={
            "acks": jtis_to_ack,
            "maxEvents": 0,
            "returnImmediately": True,
        },
        headers={
            'Authorization': 'Bearer 49e5e7785e4e4f688aa49e2585970370'
        }
    )
    print("example_polling_response_2.json:", json.dumps(ack_response.json(), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default=DEFAULT_TRANSMITTER,
                        help='Transmitter hostname')
    parser.add_argument('--no-ssl', help='Disable SSL verification for simplicity in this example code. '
                        'Do NOT do this in production.', action='store_true')

    args = parser.parse_args()

    if args.host == DEFAULT_TRANSMITTER:
        patch_hosts({ DEFAULT_TRANSMITTER: '127.0.0.1' })

    if args.no_ssl:
        with no_ssl_verification():
            main(args.host)
    else:
        main(args.host)
