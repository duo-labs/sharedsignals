import connexion

from swagger_server import business_logic

from swagger_server.models import RegisterParameters


def register(body=None):
    if connexion.request.is_json:
        body = RegisterParameters.parse_obj(connexion.request.get_json())

    token_json = business_logic.register(body.audience)
    return token_json, 200
