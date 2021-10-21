# coding: utf-8
from __future__ import absolute_import

import jwt

from flask import json

from swagger_server.business_logic import VERIFICATION_EVENT_TYPE
from swagger_server.business_logic.stream import StreamDoesNotExist
from swagger_server.controllers.stream_controller import JWKS_JSON
from swagger_server.models import PollParameters  # noqa: E501
from swagger_server.test import client, new_stream

from swagger_server import db
from swagger_server.models import RegisterParameters


def test_poll_events__no_events(client, new_stream):
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
    response_data = response.data.decode('utf-8')
    assert response.status_code == 200, 'Response body is : ' + response_data
    assert {'sets': {}, 'moreAvailable': False} == json.loads(response_data)


def test_poll_events__one_event(client, new_stream):
    """Test case for add_subject

    Request to add a subject to an Event Stream
    """
    event = {
        'jti': 'abc123',
        'iss': 'https://issuer',
        'aud': 'https://audience',
        'events': {
            VERIFICATION_EVENT_TYPE: {}
        }
    }
    new_stream.poll_queue.append(event)

    body = PollParameters(
        maxEvents=1,
        returnImmediately=True
    )

    response = client.post(
        '/poll',
        json=body.dict(exclude_none=True),
        headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )
    response_data = response.data.decode('utf-8')
    assert response.status_code == 200, 'Response body is : ' + response_data
    response_json = json.loads(response_data)
    assert 'moreAvailable' in response_json
    assert response_json['moreAvailable'] == False
    assert 'abc123' in response_json['sets']
    encoded_set = response_json['sets']['abc123']
    assert event == jwt.decode(encoded_set,
                               key=JWKS_JSON['k'],
                               algorithms=[JWKS_JSON['alg']],
                               audience='https://audience')


def test_poll_events__more_available(client, new_stream):
    """Test case for add_subject

    Request to add a subject to an Event Stream
    """
    event1 = {
        'jti': 'abc123',
        'iss': 'https://issuer',
        'aud': 'https://audience',
        'events': {
            VERIFICATION_EVENT_TYPE: {}
        }
    }
    event2 = {
        'jti': 'def456',
        'iss': 'https://issuer',
        'aud': 'https://audience',
        'events': {
            VERIFICATION_EVENT_TYPE: {}
        }
    }

    new_stream.poll_queue.append(event1)
    new_stream.poll_queue.append(event2)

    body = PollParameters(
        maxEvents=1,
        returnImmediately=True
    )

    response = client.post(
        '/poll',
        json=body.dict(exclude_none=True),
        headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )
    response_data = response.data.decode('utf-8')
    assert response.status_code == 200, 'Response body is : ' + response_data
    response_json = json.loads(response_data)
    assert 'moreAvailable' in response_json
    assert response_json['moreAvailable'] == True
    assert 'sets' in response_json
    assert len(response_json['sets']) == 1


def test_poll_events__acks(client, new_stream):
    """Test case for add_subject

    Request to add a subject to an Event Stream
    """
    event = {
        'jti': 'abc123',
        'event_type': 'https://test-event-type.com/test'
    }
    new_stream.poll_queue.append(event)

    body = PollParameters(
        maxEvents=1,
        returnImmediately=True,
        acks=['abc123']
    )

    response = client.post(
        '/poll',
        json=body.dict(exclude_none=True),
        headers={'Authorization': f'Bearer {new_stream.client_id}'}
    )
    response_data = response.data.decode('utf-8')
    assert response.status_code == 200, 'Response body is : ' + response_data
    assert {'sets': {}, 'moreAvailable': False} == json.loads(response_data)
    assert 0 == len(new_stream.poll_queue)


def test_poll_events__no_stream(client, new_stream):
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
    assert response.status_code == 404, "Incorrect response code: {}".format(response.status_code)
    assert StreamDoesNotExist(bad_client_id).message in str(response.data)


def test_jwks_json(client):
    """Test case for add_subject

    Request to add a subject to an Event Stream
    """
    response = client.get('/jwks.json')
    assert response.status_code == 200, "Incorrect response code: {}".format(response.status_code)


def test_register(client):
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
    assert response.status_code == 200, "Incorrect response code: {}".format(response.status_code)
    response_json = json.loads(response.data.decode('utf-8'))
    assert 'token' in response_json
    assert response_json['token'] in db.STREAMS


if __name__ == '__main__':
    import pytest
    pytest.main()
