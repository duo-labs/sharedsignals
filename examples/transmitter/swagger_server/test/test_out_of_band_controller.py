# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

import json

from swagger_server import db
from swagger_server.models import RegisterParameters


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
