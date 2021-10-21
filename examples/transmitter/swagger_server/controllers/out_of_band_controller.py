# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

import connexion

from swagger_server import business_logic

from swagger_server.models import RegisterParameters


def register(body=None):
    if connexion.request.is_json:
        body = RegisterParameters.parse_obj(connexion.request.get_json())

    token_json = business_logic.register(body.audience)
    return token_json, 200
