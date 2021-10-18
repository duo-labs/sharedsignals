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
