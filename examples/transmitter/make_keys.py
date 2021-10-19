import json
from pathlib import Path
import sys

from swagger_server import encryption


def make_keys(key_id: str) -> None:
    """Makes a JWKS.json file
    with a generated key for key_id if it doesn't exist
    """
    # load or create the JWKSet
    try:
        jwks = encryption.load_jwks()
    except FileNotFoundError:
        jwks = encryption.make_jwks([])

    # generate and add the key if not there already
    if not jwks.get_key(key_id):
        jwk = encryption.make_jwk(key_id)
        encryption.add_jwk_to_jwks(jwk, jwks)

    # and save it
    encryption.save_jwks(jwks)


if __name__ == "__main__":
    make_keys(key_id=sys.argv[1])
