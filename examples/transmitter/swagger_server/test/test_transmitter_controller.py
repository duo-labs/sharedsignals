# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

# coding: utf-8
from __future__ import absolute_import

from flask import json
from flask.testing import FlaskClient

from swagger_server.events import Events, VerificationEvent, SecurityEvent
from swagger_server.errors import StreamDoesNotExist
from swagger_server.business_logic.stream import Stream
from swagger_server import jwt_encode
from swagger_server.models import PollParameters
from swagger_server.test.conftest import assert_status_code


def test_poll_events__no_events(client: FlaskClient, new_stream: Stream) -> None:
    """Test case for add_subject

    Request to add a subject to an Event Stream
    """
    body = PollParameters(
        maxEvents=1,
        returnImmediately=True
    )

    response = client.post(
        '/poll',
        json=body.dict(exclude_none=True),
        headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )
    assert_status_code(response, 200)
    assert {'sets': {}, 'moreAvailable': False} == json.loads(response.data.decode('utf-8'))


def test_poll_events__one_event(client: FlaskClient, new_stream: Stream, with_jwks: None) -> None:
    """Test case for add_subject

    Request to add a subject to an Event Stream
    """
    # get the jwks file to decode the event with
    jwks = client.get('/jwks.json').json

    issuer = 'https://issuer'
    audience = 'https://audience'
    jti = 'abc123'

    SET = SecurityEvent(
        jti=jti,
        iss=issuer,
        aud=audience,
        events=Events(verification=VerificationEvent())
    )
    new_stream.queue_SET(SET)

    body = PollParameters(
        maxEvents=1,
        returnImmediately=True
    )

    response = client.post(
        '/poll',
        json=body.dict(exclude_none=True),
        headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )
    assert_status_code(response, 200)

    response_json = json.loads(response.data.decode('utf-8'))
    assert 'moreAvailable' in response_json
    assert not response_json['moreAvailable']
    assert jti in response_json['sets']
    encoded_set = response_json['sets'][jti]
    decoded_set = jwt_encode.decode_set(
        encoded_set,
        jwks=jwks,
        iss=issuer,
        aud=audience
    )

    for key in ["iss", "aud", "jti", "iat"]:
        assert decoded_set[key] == getattr(SET, key)

    assert decoded_set["events"][VerificationEvent.__uri__] == {}


def test_poll_events__more_available(client: FlaskClient, new_stream: Stream) -> None:
    """Test case for add_subject

    Request to add a subject to an Event Stream
    """
    issuer = "https://issuer.com"
    audience = "https://audience.com"

    event1 = SecurityEvent(
        iss=issuer,
        aud=audience,
        events=Events(verification=VerificationEvent())
    )
    event2 = SecurityEvent(
        iss=issuer,
        aud=audience,
        events=Events(verification=VerificationEvent())
    )

    new_stream.queue_SET(event1)
    new_stream.queue_SET(event2)

    body = PollParameters(
        maxEvents=1,
        returnImmediately=True
    )

    response = client.post(
        '/poll',
        json=body.dict(exclude_none=True),
        headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )
    assert_status_code(response, 200)

    response_json = json.loads(response.data.decode('utf-8'))
    assert 'moreAvailable' in response_json
    assert response_json['moreAvailable'] == True
    assert 'sets' in response_json
    assert len(response_json['sets']) == 1


def test_poll_events__acks(client: FlaskClient, new_stream: Stream) -> None:
    """Test case for add_subject

    Request to add a subject to an Event Stream
    """
    jti = "abc123"

    event = SecurityEvent(
        jti=jti,
        iss="http://foo.com",
        aud="http://bar.com",
        events=Events(verification=VerificationEvent())
    )

    new_stream.queue_SET(event)

    body = PollParameters(
        maxEvents=1,
        returnImmediately=True,
        acks=[jti]
    )

    response = client.post(
        '/poll',
        json=body.dict(exclude_none=True),
        headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )
    assert_status_code(response, 200)

    assert {'sets': {}, 'moreAvailable': False} == json.loads(response.data.decode('utf-8'))
    assert 0 == new_stream.count_SETs()


def test_poll_events__no_stream(client: FlaskClient, new_stream: Stream) -> None:
    """Test case for add_subject

    Request to add a subject to an Event Stream
    """
    body = PollParameters(
        maxEvents=1,
        returnImmediately=True
    )
    bad_client_id = 'IncorrectClientId'
    response = client.post(
        '/poll',
        json=body.dict(exclude_none=True),
        headers={'Authorization': f'Bearer {bad_client_id}'}
    )
    assert_status_code(response, 404)
    assert StreamDoesNotExist().message in str(response.data)


def test_jwks_json(client: FlaskClient, with_jwks: None) -> None:
    """Test case for add_subject

    Request to add a subject to an Event Stream
    """
    response = client.get('/jwks.json')
    assert_status_code(response, 200)


if __name__ == '__main__':
    import pytest
    pytest.main()
