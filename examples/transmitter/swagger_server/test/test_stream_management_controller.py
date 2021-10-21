# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

# coding: utf-8
from __future__ import absolute_import

from flask import json
import pytest

from swagger_server.business_logic.const import VERIFICATION_EVENT_TYPE
from swagger_server.business_logic.event import SUPPORTED_EVENTS
from swagger_server.business_logic.stream import Stream, StreamDoesNotExist
import swagger_server.db as db
from swagger_server.models import AddSubjectParameters
from swagger_server.models import Email
from swagger_server.models import PhoneNumber
from swagger_server.models import PollDeliveryMethod
from swagger_server.models import RemoveSubjectParameters
from swagger_server.models import StreamConfiguration
from swagger_server.models import StreamStatus
from swagger_server.models import Status
from swagger_server.models import Subject
from swagger_server.models import TransmitterConfiguration
from swagger_server.models import UpdateStreamStatus
from swagger_server.models import VerificationParameters
from swagger_server.utils import get_simple_subject


def test_add_subject(client, new_stream):
    """Test case for add_subject

    Request to add a subject to an Event Stream
    """
    body = AddSubjectParameters(subject=Email(email='new_subject@test.com'), verified=False)
    response = client.post(
        '/add-subject',
        json=body,
        headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )
    assert response.status_code == 200, 'Incorrect response code' + response.data.decode('utf-8')

    assert new_stream._subjects['new_subject@test.com'] == Status.enabled


def test_add_subject__without_email(client, new_stream):
    """Test case for add_subject

    Request to add a subject to an Event Stream, but with a subject format we don't support
    """
    body = AddSubjectParameters(subject=PhoneNumber(phone_number='17738475309'), verified=False)
    response = client.post(
        '/add-subject',
        json=body,
        headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )
    assert response.status_code == 404, 'Incorrect response code' + response.data.decode('utf-8')
    assert 'Email not found in subject' in str(response.data)


def test_add_subject__no_stream(client):
    """Test case for add_subject

    Request to add a subject to an Event Stream, but when there's no event stream for the client id given
    """
    bad_client_id = 'IncorrectClientId'
    body = AddSubjectParameters(subject=Email(email='new_subject@test.com'), verified=False)
    response = client.post(
        '/add-subject',
        json=body,
        headers={'Authorization': f'Bearer {bad_client_id}'}
    )
    assert response.status_code == 404, 'Incorrect response code' + response.data.decode('utf-8')
    assert StreamDoesNotExist().message in str(response.data)


@pytest.mark.parametrize("status", [
    Status.enabled,
    Status.paused,
    Status.disabled,
])
def test_get_status__no_subject(client, new_stream, status):
    """Test case for get_status w/out a subject

    Request to get the status of an Event Stream (no subject)
    """
    new_stream.status = status

    response = client.get(
        '/status',
        query_string={},
        headers={'Authorization': f'Bearer {new_stream.client_id}'})
    assert response.status_code == 200, 'Incorrect response code: ' + response.data.decode('utf-8')
    assert StreamStatus.parse_obj(json.loads(response.data.decode('utf-8'))) == \
        StreamStatus(status=status)


@pytest.mark.parametrize("subject", [
    Subject.parse_obj({"user": {"format": "email", "email": "foo@bar.com"}}),
    Subject.parse_obj({"format": "email", "email": "foo@bar.com"}),
    Subject.parse_obj({"identifiers": [{"format": "email", "email": "user@example.com"}]})
])
@pytest.mark.parametrize("status", [
    Status.enabled,
    Status.paused,
    Status.disabled,
])
def test_get_status__subject(client, new_stream, subject, status):
    """Test case for get_status (w/ a subject)

    Request to get the status of an Event Stream (subject included)
    """
    simple_subj = get_simple_subject(subject, Email)
    email_address = simple_subj.email
    new_stream.add_subject(email_address)
    new_stream.set_subject_status(email_address, status)

    response = client.get(
        '/status',
        query_string={'subject': subject.json()} if subject else None,
        headers={'Authorization': f'Bearer {new_stream.client_id}'})
    assert response.status_code == 200, 'Incorrect response code: ' + response.data.decode('utf-8')
    assert StreamStatus.parse_obj(json.loads(response.data.decode('utf-8'))) == \
        StreamStatus(
            status=status,
            subject=subject,
        )


def test_get_status__no_stream(client):
    """Test case for get_status

    Request to get the status of a non-existent Event Stream
    """
    bad_client_id = 'IncorrectClientId'
    response = client.get(
        '/status',
        query_string=None,
        headers={'Authorization': f'Bearer {bad_client_id}'})
    assert response.status_code == 404, 'Incorrect response code: ' + response.data.decode('utf-8')
    assert StreamDoesNotExist().message in str(response.data)


def test_remove_subject(client, new_stream):
    """Test case for remove_subject

    Request to remove a subject from an Event Stream
    """
    new_stream._subjects['old_subject@test.com'] = Status.enabled

    body = RemoveSubjectParameters(subject=Email(email="old_subject@test.com"))
    response = client.post(
        '/remove-subject',
        json=body,
        headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )

    assert response.status_code == 204, 'Incorrect response code' + response.data.decode('utf-8')

    assert "old_subject@test.com" not in new_stream._subjects


def test_remove_subject__without_email(client, new_stream):
    """Test case for remove_subject

    Request to remove subject from an Event Stream, but with a subject format we don't support
    """
    body = RemoveSubjectParameters(subject=PhoneNumber(phone_number='17738475309'))
    response = client.post(
        '/remove-subject',
        json=body,
        headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )

    assert response.status_code == 404, 'Incorrect response code' + response.data.decode('utf-8')
    assert 'Email not found in subject' in str(response.data)


def test_remove_subject__no_stream(client):
    """Test case for add_subject

    Request to remove a subject from an Event Stream, but when there's no event stream for the client id given
    """
    bad_client_id = 'IncorrectClientId'
    body = RemoveSubjectParameters(subject=Email(email="old_subject@test.com"))
    response = client.post(
        '/remove-subject',
        json=body,
        headers={'Authorization': f'Bearer {bad_client_id}'}
    )
    assert response.status_code == 404, 'Incorrect response code' + response.data.decode('utf-8')
    assert StreamDoesNotExist().message in str(response.data)


def test_stream_post(client, new_stream):
    """Test case for stream_post

    Request to update the configuration of an event stream
    """
    old_config = new_stream.config.copy()
    requested_events = SUPPORTED_EVENTS.copy()
    requested_events.pop()  # remove session revoked
    requested_events.append('https://schemas.openid.net/fake-event')
    new_config = StreamConfiguration(
        iss='http://pets.com',  # this should not update
        events_requested=requested_events,
        delivery=PollDeliveryMethod(endpoint_url="")
    )

    response = client.post(
        '/stream',
        json=new_config.dict(exclude_none=True),
        headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )
    assert response.status_code == 200, \
                   'Response body is : ' + response.data.decode('utf-8')

    updated_stream = Stream.load(new_stream.client_id)

    assert updated_stream.config.iss == old_config.iss
    assert updated_stream.config.iss != new_config.iss
    assert updated_stream.config.aud == old_config.aud
    assert updated_stream.config.events_supported == old_config.events_supported
    assert updated_stream.config.events_requested == requested_events

    expected_delivered = SUPPORTED_EVENTS.copy()
    expected_delivered.pop()
    assert updated_stream.config.events_delivered == expected_delivered

    assert "/poll" in updated_stream.config.delivery.endpoint_url


def test_stream_post__no_stream(client):
    """Test case for stream_post

    Request to update the configuration of an event stream, but the event stream doesn't exist.
    """
    bad_client_id = 'IncorrectClientId'
    response = client.post(
        '/stream',
        json={},
        headers={'Authorization': f'Bearer {bad_client_id}'}
    )
    assert response.status_code == 404, 'Incorrect response code' + response.data.decode('utf-8')
    assert StreamDoesNotExist().message in str(response.data)


def test_stream_delete(client, new_stream):
    """Test case for stream_delete

    Request to remove the configuration of an event stream
    """
    response = client.delete(
        '/stream', headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )
    assert response.status_code == 200, 'Incorrect response code' + response.data.decode('utf-8')

    assert new_stream.client_id not in db.STREAMS


def test_stream_delete__no_stream(client):
    """Test case for stream_delete

    Request to remove the configuration of an event stream, passes even if there's no stream
    """
    bad_client_id = 'IncorrectClientId'
    response = client.delete('/stream', headers={'Authorization': f'Bearer {bad_client_id}'}
    )
    assert response.status_code == 200, 'Incorrect response code' + response.data.decode('utf-8')


def test_stream_get(client, new_stream):
    """Test case for stream_get

    Request to retrieve the configuration of an event stream
    """
    # attempt to get the stream
    response = client.open(
        '/stream',
        method='GET',
        headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )
    assert response.status_code == 200, \
                   'Response body is : ' + response.data.decode('utf-8')


def test_stream_get__no_stream(client):
    """Test case for stream_get

    Request to retrieve the configuration of an event stream, but when there's no event stream for the client id given
    """
    bad_client_id = 'IncorrectClientId'
    # attempt to get the stream
    response = client.open(
        '/stream',
        method='GET',
        headers={'Authorization': f'Bearer {bad_client_id}'}
    )
    assert response.status_code == 404, 'Incorrect response code' + response.data.decode('utf-8')
    assert StreamDoesNotExist().message in str(response.data)


@pytest.mark.parametrize("subject", [
    Subject.parse_obj({"user": {"format": "email", "email": "foo@bar.com"}}),
    Subject.parse_obj({"format": "email", "email": "foo@bar.com"}),
    Subject.parse_obj({"identifiers": [{"format": "email", "email": "user@example.com"}]})
])
@pytest.mark.parametrize("status", [
    Status.enabled,
    Status.paused,
    Status.disabled,
])
def test_update_status__subject(client, new_stream, subject, status):
    """Test case for update_status

    Request to update an Event Stream's status
    """
    simple_subj = get_simple_subject(subject, Email)
    email_address = simple_subj.email
    new_stream.add_subject(email_address)

    body = UpdateStreamStatus(
        status=status,
        subject=subject,
        reason='administrator action',
    )
    response = client.post(
        '/status',
        json=body.dict(exclude_none=True),
        headers={'Authorization': f'Bearer {new_stream.client_id}'})
    assert response.status_code == 200, 'Incorrect response code' + response.data.decode('utf-8')
    assert StreamStatus.parse_obj(json.loads(response.data.decode('utf-8'))) == \
        StreamStatus(
            status=status,
            subject=body.subject,
        )
    assert new_stream.get_subject_status(email_address) == status


@pytest.mark.parametrize("status", [
    Status.enabled,
    Status.paused,
    Status.disabled,
])
def test_update_status__no_subject(client, new_stream, status):
    """Test case for update_status

    Request to update an Event Stream's status
    """
    body = UpdateStreamStatus(
        status=status,
        reason='administrator action',
    )
    response = client.post(
        '/status',
        json=body.dict(exclude_none=True),
        headers={'Authorization': f'Bearer {new_stream.client_id}'})
    assert response.status_code == 200, 'Incorrect response code' + response.data.decode('utf-8')
    assert StreamStatus.parse_obj(json.loads(response.data.decode('utf-8'))) == \
        StreamStatus(
            status=status,
            subject=body.subject,
        )
    assert new_stream.status == status


@pytest.mark.parametrize(
    "state", [
        None,
        "someArbitraryString"
    ]
)
def test_verification_request__polling(client, new_stream, state):
    """Test case for verification_request

    Request that a verification event be sent over an Event Stream
    """
    new_stream.config.delivery = PollDeliveryMethod(endpoint_url="http://transmitter.com/polling"),

    body = VerificationParameters(state=state)
    response = client.post(
        '/verification',
        json=body.dict(exclude_none=True),
        headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )
    assert response.status_code == 204, "Incorrect response code: {}".format(response.status_code)

    assert len(new_stream.poll_queue) == 1, "Incorrect queue size: {}".format(stream_queue.qsize())
    events = new_stream.poll_queue[0]

    assert VERIFICATION_EVENT_TYPE in events['events']
    verification_event = events['events'][VERIFICATION_EVENT_TYPE]

    if state:
        assert verification_event['state'] == state, verification_event
    else:
        assert 'state' not in verification_event


def test_verification_request__no_stream(client):
    """Test case for verification_request

    Request that a verification event be sent over an Event Stream, but when there's no event stream for the client id given
    """
    bad_client_id = 'IncorrectClientId'
    # TODO: This should also work when no state is specified, but current errors:
    #       ERROR connexion.decorators.validation:validation.py:200 http://localhost/verification validation error:
    #             None is not of type 'string' - 'state
    body = VerificationParameters(state="someArbitraryString")
    response = client.post(
        '/verification',
        json=body,
        headers={'Authorization': f'Bearer {bad_client_id}'}
    )
    assert response.status_code == 404, "Incorrect response code: {}".format(response.status_code)
    assert StreamDoesNotExist().message in str(response.data)


def test_well_known_sse_configuration_get(client):
    """Test case for well_known_sse_configuration_get

    Transmitter Configuration Request (without path)
    """
    response = client.get('/.well-known/sse-configuration')
    assert response.status_code == 200, "Incorrect response code: {}".format(response.status_code)


def test_well_known_sse_configuration_issuer_get(client):
    """Test case for well_known_sse_configuration_issuer_get

    Transmitter Configuration Request (with path)
    """
    response = client.get('/.well-known/sse-configuration/{issuer}'.format(issuer='issuer_example'))
    assert response.status_code == 200, "Incorrect response code: {}".format(response.status_code)
    config = TransmitterConfiguration.parse_obj(json.loads(response.data.decode('utf-8')))
    assert config.issuer.split("/")[-1] == "issuer_example", "Incorrect issuer: {}".format(config.issuer)


if __name__ == '__main__':
    import pytest
    pytest.main()
