import uuid
import requests


class TransmitterClient:
    """A class that holds information for interacting with the transmitter"""

    def __init__(self, sse_config: dict[str, str], verify: bool, audience: str, bearer: str):
        # FIXME get issuer information
        self.sse_config = sse_config
        self.verify = verify
        self.audience = audience
        self.auth = {"Authorization": f"Bearer {bearer}"}

    def configure_stream(self):
        """ Configure stream and return the current config """
        config_response = requests.post(
            url=self.sse_config["configuration_endpoint"],
            verify=self.verify,
            json={
                'delivery': {
                    'method': 'https://schemas.openid.net/secevent/risc/delivery-method/push',
                    'endpoint_url': "http://receiver:5003/event"
                },
                'events_requested': [
                    'https://schemas.openid.net/secevent/risc/event-type/credential-compromise',
                ]
            },
            headers=self.auth,
        )
        config_response.raise_for_status()

        requests.post(
            url=self.sse_config["add_subject_endpoint"],
            verify=self.verify,
            json={
                'subject': {
                    'format': 'email',
                    'email': '*'
                }
            },
            headers=self.auth
        )
        return config_response.json()

    def request_verification(self):
        """ Request a single verification event """
        return requests.post(
            url=self.sse_config["verification_endpoint"],
            verify=self.verify,
            json={'state': uuid.uuid4().hex},
            headers=self.auth,
        )
