# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.
from typing import Dict, List, Any, Tuple, Union

import connexion

from swagger_server import business_logic
from swagger_server import jwt_encode
from swagger_server.models import PollParameters


def poll_events(token_info: Dict[str, str]) -> Tuple[Dict[str, Any], int]:
    """Request to return queued events"""

    client_id = token_info['client_id']
    body = PollParameters.parse_obj(connexion.request.get_json())

    events, more_available = business_logic.poll_request(
        body.maxEvents, body.returnImmediately, body.acks, client_id
    )

    set_events = {
        'sets': {
            event.jti: jwt_encode.encode_set(event) for event in events
        },
        'moreAvailable': more_available
    }

    return set_events, 200


def jwks_json() -> Tuple[Dict[str, Any], int]:
    """
    :return: JSON Web Key Set for our Event Transmitter
    """
    # Export the JWKS _without_ the private keys used to encode the SETs
    jwks = jwt_encode.load_jwks().export(private_keys=False, as_dict=True)
    return jwks, 200
