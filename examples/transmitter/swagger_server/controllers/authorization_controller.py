# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

"""
controller generated to handled auth operation described at:
https://connexion.readthedocs.io/en/latest/security.html
"""

from typing import Dict, Any

from werkzeug.exceptions import Unauthorized

from swagger_server import db
from swagger_server.errors import StreamDoesNotExist


def check_BearerAuth(token: str) -> Dict[str, Any]:
    """Get the client ID from the dict of known tokens. Raise an error if
    token is unknown
    """
    if not db.stream_exists(token):
        raise StreamDoesNotExist()

    return {
        'client_id': token,
        'active': True,
    }
