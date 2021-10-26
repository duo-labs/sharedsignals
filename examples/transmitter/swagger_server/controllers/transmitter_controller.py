# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

import connexion

from swagger_server import business_logic
from swagger_server.business_logic.stream import StreamDoesNotExist
from swagger_server import jwt_encode
from swagger_server.models import PollParameters


def poll_events(token_info, body=None):
    """Request to return queued events

    :param body: Optional request parameters
    :type body: dict | bytes

    :rtype: None
    """
    client_id = token_info['client_id']

    if connexion.request.is_json:
        body = PollParameters.parse_obj(connexion.request.get_json())

    try:
        events, more_available = business_logic.poll_request(
            body.maxEvents, body.returnImmediately, body.acks, client_id
        )
    except StreamDoesNotExist as e:
        return e.message, 404

    events = {
        'sets': {
            event['jti']: jwt_encode.encode_set(event) for event in events
        },
        'moreAvailable': more_available
    }

    return events, 200


def jwks_json():
    """
    :return: JSON Web Key Set for our Event Transmitter
    """
    # Export the JWKS _without_ the private keys used to encode the SETs
    jwks = jwt_encode.load_jwks().export(private_keys=False, as_dict=True)
    return jwks, 200
