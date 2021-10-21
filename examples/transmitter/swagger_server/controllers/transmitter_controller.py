# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Licensed under BSD 3-Clause License

import connexion
import jwt

from swagger_server import business_logic
from swagger_server.business_logic import StreamDoesNotExist
from swagger_server.models import PollParameters


JWKS_JSON = {
    "kty": "oct",
    "alg": "HS256",
    "k": "AyM1SysPpbyDfgZld3umj1qzKObwVMkoqQ-EstJQLr_T-1qS0gZH75aKtMN3Yj0iPS4hcgUuTwjAzZr1Z9CAow"
}


def poll_events(token_info, body=None):  # noqa: E501
    """Request to return queued events

     # noqa: E501

    :param body: Optional request parameters
    :type body: dict | bytes

    :rtype: None
    """
    client_id = token_info['client_id']

    if connexion.request.is_json:
        body = PollParameters.parse_obj(connexion.request.get_json())

    try:
        events, more_available = business_logic.poll_request(body.maxEvents, body.returnImmediately, body.acks, client_id)
    except StreamDoesNotExist as e:
        return e.message, 404

    events = {
        'sets': {
            event['jti']: jwt.encode(event, JWKS_JSON['k'], JWKS_JSON['alg']) for event in events
        },
        'moreAvailable': more_available
    }

    return events, 200


def jwks_json():
    """
    :return: JSON Web Key Set for our Event Transmitter
    """
    return JWKS_JSON
