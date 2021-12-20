# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

import json

from flask.testing import FlaskClient

from swagger_server import db
from swagger_server.models import RegisterParameters
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


if __name__ == '__main__':
    import pytest
    pytest.main()
