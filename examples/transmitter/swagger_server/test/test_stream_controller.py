# coding: utf-8
from __future__ import absolute_import

from flask import json

from swagger_server.business_logic import VERIFICATION_EVENT_TYPE
from swagger_server.business_logic.stream import StreamDoesNotExist
from swagger_server import jwt_encode
from swagger_server.models import PollParameters


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


def test_poll_events__one_event(client, new_stream, with_jwks):
    """Test case for add_subject

    Request to add a subject to an Event Stream
    """
    # get the jwks file to decode the event with
    jwks = client.get('/jwks.json').json

    issuer = 'https://issuer'
    audience = 'https://audience'

    event = {
        'jti': 'abc123',
        'iss': issuer,
        'aud': audience,
        'events': {
            VERIFICATION_EVENT_TYPE: {}
        }
    }
    new_stream.poll_queue.put(event)

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
    assert not response_json['moreAvailable']
    assert 'abc123' in response_json['sets']
    encoded_set = response_json['sets']['abc123']
    decoded_set = jwt_encode.decode_set(
        encoded_set,
        jwks=jwks,
        iss=issuer,
        aud=audience
    )
    assert event == decoded_set


def test_poll_events__acks(client, new_stream):
    """Test case for add_subject

    Request to add a subject to an Event Stream
    """
    event = {
        'jti': 'abc123',
        'event_type': 'https://test-event-type.com/test'
    }
    new_stream.poll_queue.put(event)

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
    assert 0 == new_stream.poll_queue.qsize()


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
    assert response.status_code == 404, 'Incorrect response code: ' + response.data.decode('utf-8')
    assert StreamDoesNotExist(bad_client_id).message in str(response.data)


def test_jwks_json(client, with_jwks):
    """Test case for add_subject

    Request to add a subject to an Event Stream
    """
    response = client.get('/jwks.json')
    err_msg = "Incorrect response code: {}".format(response.status_code)
    assert response.status_code == 200, err_msg


if __name__ == '__main__':
    import pytest
    pytest.main()
