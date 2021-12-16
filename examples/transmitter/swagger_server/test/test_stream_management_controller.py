# coding: utf-8
# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.
from __future__ import absolute_import
from typing import Any, Dict, Optional
from unittest.mock import patch

from flask import json
from flask.testing import FlaskClient
import pytest
import requests

from swagger_server.business_logic.const import VERIFICATION_EVENT_TYPE, POLL_ENDPOINT
from swagger_server.events import SUPPORTED_EVENTS, SecurityEvent, Events, VerificationEvent
from swagger_server.business_logic.stream import Stream
from swagger_server.errors import StreamDoesNotExist, SubjectNotInStream
import swagger_server.db as db
from swagger_server.models import AddSubjectParameters
from swagger_server.models import Email
from swagger_server.models import PhoneNumber
from swagger_server.models import PollDeliveryMethod
from swagger_server.models import PushDeliveryMethod
from swagger_server.models import RemoveSubjectParameters
from swagger_server.models import StreamConfiguration
from swagger_server.models import StreamStatus
from swagger_server.models import Status
from swagger_server.models import Subject
from swagger_server.models import TransmitterConfiguration
from swagger_server.models import UpdateStreamStatus
from swagger_server.models import VerificationParameters
from swagger_server import jwt_encode
from swagger_server.utils import get_simple_subject


def test_add_subject(client: FlaskClient, new_stream: Stream) -> None:
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

    assert new_stream.get_subject_status('new_subject@test.com') == Status.enabled


def test_add_subject__without_email(client: FlaskClient, new_stream: Stream) -> None:
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


def test_add_subject__no_stream(client: FlaskClient) -> None:
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
def test_get_status__no_subject(client: FlaskClient, new_stream: Stream, status: Status) -> None:
    """Test case for get_status w/out a subject

    Request to get the status of an Event Stream (no subject)
    """
    new_stream.status = status
    new_stream.save()

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
def test_get_status__subject(client: FlaskClient, new_stream: Stream, 
                             subject: Subject, status: Status) -> None:
    """Test case for get_status (w/ a subject)

    Request to get the status of an Event Stream (subject included)
    """
    simple_subj = get_simple_subject(subject, Email)
    assert simple_subj is not None
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


def test_get_status__no_stream(client: FlaskClient) -> None:
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


def test_remove_subject(client: FlaskClient, new_stream: Stream) -> None:
    """Test case for remove_subject

    Request to remove a subject from an Event Stream
    """
    email = "old_subject@test.com"
    new_stream.add_subject(email)

    body = RemoveSubjectParameters(subject=Email(email=email))
    response = client.post(
        '/remove-subject',
        json=body,
        headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )

    assert response.status_code == 204, 'Incorrect response code' + response.data.decode('utf-8')

    with pytest.raises(SubjectNotInStream):
        new_stream.get_subject_status(email)


def test_remove_subject__without_email(client: FlaskClient, new_stream: Stream) -> None:
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


def test_remove_subject__no_stream(client: FlaskClient) -> None:
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


def test_stream_post(client, new_stream: Stream) -> None:
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
        delivery=PollDeliveryMethod(endpoint_url=None)
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


def test_stream_post__no_stream(client: FlaskClient) -> None:
    """Test case for stream_post

    Request to update the configuration of an event stream, but the event stream doesn't exist.
    """
    bad_client_id = 'IncorrectClientId'
    new_config = StreamConfiguration(
        events_requested=SUPPORTED_EVENTS.copy(),
        delivery=PollDeliveryMethod(endpoint_url=None)
    )
    response = client.post(
        '/stream',
        json=new_config.dict(exclude_none=True),
        headers={'Authorization': f'Bearer {bad_client_id}'}
    )
    assert response.status_code == 404, 'Incorrect response code' + response.data.decode('utf-8')
    assert StreamDoesNotExist().message in str(response.data)


def test_stream_delete(client: FlaskClient, new_stream: Stream) -> None:
    """Test case for stream_delete

    Request to remove the configuration of an event stream
    """
    # add a subject
    email = "foo@bar.com"
    new_stream.add_subject(email)
    assert new_stream.get_subject_status(email) == Status.enabled

    # add a SET
    SET = SecurityEvent(
        events=Events(verification=VerificationEvent())
    )
    new_stream.queue_SET(SET)
    assert new_stream.count_SETs() == 1

    # update the config
    new_config = StreamConfiguration(
        format="opaque",
        events_requested=SUPPORTED_EVENTS.copy(),
        delivery=PollDeliveryMethod(endpoint_url=None)
    )
    assert new_stream.config.format is None
    new_stream.update_config(new_config)
    assert new_stream.config.format == "opaque"

    response = client.delete(
        '/stream', headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )
    assert response.status_code == 200, 'Incorrect response code' + response.data.decode('utf-8')

    # show that the SETs and subjects have been erased
    updated_stream = Stream.load(new_stream.client_id)
    assert updated_stream.count_SETs() == 0
    with pytest.raises(SubjectNotInStream):
        updated_stream.get_subject_status(email)

    # show that the stream's config has been reset
    assert updated_stream.config.format is None



# def test_stream_delete__no_stream(client: FlaskClient) -> None:
#     """Test case for stream_delete

#     Request to remove the configuration of an event stream, passes even if there's no stream
#     """
#     bad_client_id = 'IncorrectClientId'
#     response = client.delete('/stream', headers={'Authorization': f'Bearer {bad_client_id}'})
#     assert response.status_code == 200, 'Incorrect response code' + response.data.decode('utf-8')


def test_stream_get(client: FlaskClient, new_stream: Stream) -> None:
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


def test_stream_get__no_stream(client: FlaskClient) -> None:
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
def test_update_status__subject(client: FlaskClient, new_stream: Stream,
                                subject: Subject, status: Status) -> None:
    """Test case for update_status

    Request to update an Event Stream's status
    """
    simple_subj = get_simple_subject(subject, Email)
    assert simple_subj is not None
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
def test_update_status__no_subject(client: FlaskClient, new_stream: Stream, status: Status) -> None:
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
    updated_stream = Stream.load(new_stream.client_id)
    assert updated_stream.status == status


@pytest.mark.parametrize(
    "state", [
        None,
        "someArbitraryString"
    ]
)
def test_verification_request__polling(client: FlaskClient, new_stream: Stream, 
                                       state: Optional[str]) -> None:
    """Test case for verification_request

    Request that a verification event be sent over an Event Stream
    """
    new_stream.config.delivery = PollDeliveryMethod(endpoint_url="http://transmitter.com/polling")

    body = VerificationParameters(state=state)
    response = client.post(
        '/verification',
        json=body.dict(exclude_none=True),
        headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )
    assert response.status_code == 204, "Incorrect response code: {}".format(response.status_code)

    n_SETs = new_stream.count_SETs()
    assert n_SETs == 1, f"Incorrect queue size: {n_SETs}"
    SETs = new_stream.get_SETs()

    verification_event = SETs[0].events.verification

    if state:
        assert verification_event.state == state, verification_event
    else:
        assert verification_event.state is None


def test_verification_request__pushing__no_response(client: FlaskClient, new_stream: Stream) -> None:
    """Test case for verification_request

    Request that a verification event be sent over an Event Stream with Push delivery method,
    but the push delivery fails, the response to the request must still return 204
    """
    push_url = "https://test-case.popular-app.com/push"
    new_stream.config.delivery = PushDeliveryMethod(endpoint_url=push_url)
    new_stream.save()

    body = VerificationParameters(state=None)

    with patch('requests.post', side_effect=requests.Timeout()) as post_mock:
        response = client.post(
            '/verification',
            json=body.dict(exclude_none=True),
            headers={'Authorization': f'Bearer {new_stream.client_id}'}
        )

    assert response.status_code == 204, "Incorrect response code: {}".format(response.status_code) + response.data.decode('utf-8')

    post_mock.assert_called_once()


@pytest.mark.parametrize(
    "auth_header", [ None, "test-auth-header" ]
)
def test_verification_request__pushing(client: FlaskClient, new_stream: Stream, 
                                       auth_header: Optional[str]) -> None:
    """Test case for verification_request

    Request that a verification event be sent over an Event Stream with Push delivery method
    """
    push_url = "https://test-case.popular-app.com/push"
    new_stream.config.delivery = PushDeliveryMethod(
        endpoint_url=push_url, 
        authorization_header=auth_header
    )
    new_stream.save()

    state = "test state"
    body = VerificationParameters(state=state)

    with patch('requests.post') as post_mock:
        response = client.post(
            '/verification',
            json=body.dict(exclude_none=True),
            headers={'Authorization': f'Bearer {new_stream.client_id}'}
        )

    assert response.status_code == 204, "Incorrect response code: {}".format(response.status_code) + response.data.decode('utf-8')

    post_mock.assert_called_once()

    args = post_mock.call_args

    assert push_url == str(args.args[0])

    if auth_header:
        assert 'headers' in args.kwargs
        headers = { k.lower(): v for k, v in args.kwargs['headers'].items()}
        assert 'authorization' in headers
        assert headers['authorization'] == auth_header

    assert 'data' in args.kwargs

    jwks = client.get('/jwks.json').json
    iss = new_stream.config.iss
    aud = new_stream.config.aud

    event = jwt_encode.decode_set(args.kwargs['data'], jwks, iss, aud)
    assert VERIFICATION_EVENT_TYPE in event['events']
    assert event['events'][VERIFICATION_EVENT_TYPE]['state'] == state


def test_verification_request__no_stream(client: FlaskClient) -> None:
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


def test_well_known_sse_configuration_get(client: FlaskClient) -> None:
    """Test case for well_known_sse_configuration_get

    Transmitter Configuration Request (without path)
    """
    response = client.get('/.well-known/sse-configuration')
    assert response.status_code == 200, "Incorrect response code: {}".format(response.status_code)


def test_well_known_sse_configuration_issuer_get(client: FlaskClient) -> None:
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
