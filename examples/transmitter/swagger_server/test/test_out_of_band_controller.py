import json

from swagger_server import db
from swagger_server.models import RegisterParameters
from swagger_server.test import client, new_stream


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
