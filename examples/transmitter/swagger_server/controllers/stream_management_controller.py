# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

import logging
from typing import Dict, Any, Optional, Tuple, Union

import connexion
from connexion import NoContent

from swagger_server import business_logic
from swagger_server.models import AddSubjectParameters  # noqa: E501
from swagger_server.models import RemoveSubjectParameters  # noqa: E501
from swagger_server.models import StreamConfiguration  # noqa: E501
from swagger_server.models import Subject  # noqa: E501
from swagger_server.models import UpdateStreamStatus  # noqa: E501
from swagger_server.models import VerificationParameters  # noqa: E501
from swagger_server.models import StreamStatus
from swagger_server.models import TransmitterConfiguration


log = logging.getLogger(__name__)


def add_subject(token_info: Dict[str, str]) -> Tuple[Any, int]:  # noqa: E501
    """Request to add a subject to an Event Stream

    [Spec](https://openid.net/specs/openid-sse-framework-1_0.html#adding-a-subject-to-a-stream)  Event Receivers can send requests to an Event Transmitter&#x27;s Add Subject endpoint to add a subject to an Event Stream. # noqa: E501
    """
    client_id = token_info['client_id']
    body = AddSubjectParameters.parse_obj(connexion.request.get_json())

    business_logic.add_subject(
        subject=body.subject, verified=body.verified, client_id=client_id
    )
    return NoContent, 200


def get_status(token_info: Dict[str, str],
               subject: Optional[bytes] = None) -> Tuple[Any, int]:  # noqa: E501
    """Request to get the status of an Event Stream

    [Spec](https://openid.net/specs/openid-sse-framework-1_0.html#reading-a-streams-status)  An Event Receiver checks the current status of an event stream by making an HTTP GET request to the stream’s Status Endpoint. # noqa: E50
    """
    client_id = token_info['client_id']

    subject_parsed = None
    if subject:
        subject_parsed = Subject.parse_raw(subject)

    return business_logic.get_status(subject=subject_parsed,
                                     client_id=client_id), 200


def remove_subject(token_info: Dict[str, str]) -> Tuple[Any, int]:  # noqa: E501
    """Request to add a subject to an Event Stream

    [Spec](https://openid.net/specs/openid-sse-framework-1_0.html#removing-a-subject)  Event Receivers can send requests to an Event Transmitter&#x27;s Remove Subject endpoint to remove a subject from an Event Stream. # noqa: E501
    """
    client_id = token_info['client_id']
    body = RemoveSubjectParameters.parse_obj(connexion.request.get_json())

    business_logic.remove_subject(
        subject=body.subject, client_id=client_id
    )
    return NoContent, 204


def stream_post(token_info: Dict[str, str]) -> Tuple[StreamConfiguration, int]:  # noqa: E501
    """Request to update the configuration of an event stream

    [Spec](https://openid.net/specs/openid-sse-framework-1_0.html#updating-a-streams-configuration)  An Event Receiver updates the current configuration of a stream by making an HTTP POST request to the Configuration Endpoint. The POST body contains a JSON representation of the updated configuration. On receiving a valid request the Event Transmitter responds with a 200 OK response containing a JSON representation of the updated stream configuration in the body.  The full set of editable properties must be present in the POST body, not only the ones that are specifically intended to be changed. Missing properties SHOULD be interpreted as requested to be deleted. Event Receivers should read the configuration first, modify the JSON representation, then make an update request.  Properties that cannot be updated MAY be present, but they MUST match the expected value. # noqa: E501
    """
    client_id = token_info['client_id']
    body = StreamConfiguration.parse_obj(connexion.request.get_json())

    new_config = business_logic.stream_post(body, client_id)
    return new_config, 200


def stream_delete(token_info: Dict[str, str]) -> Tuple[Any, int]:
    """Request to remove the configuration of an event stream

    An Event Receiver removes the configuration of a stream by making an HTTP DELETE request to the Configuration Endpoint. On receiving a request the Event Transmitter responds with a 200 OK response if the configuration was successfully removed. # noqa: E501
    """
    client_id = token_info['client_id']
    business_logic.stream_delete(client_id=client_id)

    # always return 200, even if stream did not exist
    return NoContent, 200


def stream_get(token_info: Dict[str, str]) -> Tuple[StreamConfiguration, int]:
    """Request to retrieve the configuration of an event stream

    [Spec](https://openid.net/specs/openid-sse-framework-1_0.html#reading-a-streams-configuration)  An Event Receiver gets the current configuration of a stream by making an HTTP GET request to the Configuration Endpoint. On receiving a valid request the Event Transmitter responds with a 200 OK response containing a JSON representation of the stream’s configuration in the body. # noqa: E501
    """
    client_id = token_info['client_id']
    return business_logic.stream_get(client_id=client_id), 200


def update_status(token_info: Dict[str, str]) -> Tuple[StreamStatus, int]:  # noqa: E501
    """Request to update an Event Stream&#x27;s status

    [Spec](https://openid.net/specs/openid-sse-framework-1_0-ID1.html#updating-a-streams-status)  An Event Receiver updates the current status of a stream by making an HTTP POST request to the Status Endpoint. # noqa: E501
    """
    client_id = token_info['client_id']
    body = UpdateStreamStatus.parse_obj(connexion.request.get_json())

    new_status = business_logic.update_status(
        status=body.status,
        subject=body.subject,
        reason=body.reason,
        client_id=client_id,
    )
    return new_status, 200


def verification_request(token_info: Dict[str, str]) -> Tuple[Any, int]:  # noqa: E501
    """Request that a verification event be sent over an Event Stream"""

    client_id = token_info['client_id']
    body = VerificationParameters.parse_obj(connexion.request.get_json())

    business_logic.verification_request(
        state=body.state, client_id=client_id
    )
    return NoContent, 204


def _well_known_sse_configuration_get() -> Tuple[TransmitterConfiguration, int]:  # noqa: E501
    """Transmitter Configuration Request (without path)

    Return Transmitter Configuration information. # noqa: E501
    """
    config = business_logic._well_known_sse_configuration_get(
        connexion.request.url_root
    )

    return config, 200


def _well_known_sse_configuration_issuer_get(issuer: str) -> Tuple[TransmitterConfiguration, int]:  # noqa: E501
    """Transmitter Configuration Request (with path)

    Return Transmitter Configuration information (with support for specifying an issuer). # noqa: E501
    """
    config = business_logic._well_known_sse_configuration_get(
        connexion.request.url_root, issuer=issuer
    )
    return config, 200
