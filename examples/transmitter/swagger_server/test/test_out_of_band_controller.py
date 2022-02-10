# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

import json

from flask.testing import FlaskClient

import pytest

from swagger_server import db
from swagger_server.models import (
    AddSubjectParameters, EventType, PollDeliveryMethod,
    RegisterParameters, StreamConfiguration,
    Subject, TriggerEventParameters
)
from swagger_server.test.conftest import assert_status_code


def test_register(client: FlaskClient) -> None:
    """Test case for add_subject

    Request to add a subject to an Event Stream
    """
    body = RegisterParameters(
        audience='https://popular-app.com'
    )
    response = client.post(
        '/register',
        json=body.dict(exclude_none=True)
    )
    assert_status_code(response, 200)
    response_json = json.loads(response.data.decode('utf-8'))
    assert 'token' in response_json
    assert db.stream_exists(response_json['token'])


@pytest.mark.parametrize("subject", [
    Subject.parse_obj({"user": {"format": "email", "email": "foo@bar.com"}}),
    Subject.parse_obj({"format": "email", "email": "foo@bar.com"}),
    Subject.parse_obj({"identifiers": [{"format": "email",
                                        "email": "user@example.com"}]})
])
@pytest.mark.parametrize("event_type", [
    EventType.session_revoked,
    EventType.token_claims_change,
    EventType.credential_change,
    EventType.assurance_level_change,
    EventType.device_compliance_change,
    EventType.account_purged,
    EventType.account_disabled,
    EventType.account_enabled,
    EventType.identifier_changed,
    EventType.identifier_recycled,
    EventType.opt_in,
    EventType.opt_out_initiated,
    EventType.opt_out_cancelled,
    EventType.opt_out_effective,
    EventType.recovery_activated,
    EventType.recovery_information_changed,
    EventType.RISC_sessions_revoked
])
def test_trigger_event(client: FlaskClient, subject: Subject,
                       event_type: EventType) -> None:
    """Test case for trigger_event

    Request to generate a security event other than verification
    """
    # register a stream
    body = RegisterParameters(
        audience='https://popular-app.com'
    )
    register_response = client.post(
        '/register',
        json=body.dict(exclude_none=True)
    )
    register_response_json = json.loads(register_response.data.decode('utf-8'))
    assert db.stream_exists(register_response_json['token'])

    # Set stream to poll
    new_config = StreamConfiguration(
        iss='http://pets.com',  # this should not update
        events_requested=[],
        delivery=PollDeliveryMethod(
            endpoint_url="http://transmitter.com/polling"),
        subject=subject
    )

    response = client.post(
        '/stream',
        json=new_config.dict(exclude_none=True),
        headers={'Authorization': f'Bearer {register_response_json["token"]}'}
    )
    assert_status_code(response, 200)

    # add subject
    body = AddSubjectParameters(subject=subject, verified=False)
    response = client.post(
        '/add-subject',
        json=body,
        headers={'Authorization': f'Bearer {register_response_json["token"]}'}
    )
    assert response.status_code == 200

    # trigger event
    body = TriggerEventParameters(
        event_type=event_type,
        subject=subject
    )
    response = client.post(
        '/trigger-event',
        json=body
    )
    assert_status_code(response, 200)
    # # check if event is queued
    num_SETs = db.count_SETs(client_id=register_response_json["token"])
    assert num_SETs


if __name__ == '__main__':
    pytest.main()
