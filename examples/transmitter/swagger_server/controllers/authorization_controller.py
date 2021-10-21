# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a
# BSD 3-Clause License that can be found in the LICENSE file.

"""
controller generated to handled auth operation described at:
https://connexion.readthedocs.io/en/latest/security.html
"""


def check_BearerAuth(token):
    # For now, we accept any token and we let the client ID be equal
    # to the token value.
    # TODO: actually set up clients and use encoding to check these things
    return dict(
        active=True,
        client_id=token
    )
