import requests
import json

from utils import no_ssl_verification


if __name__ == '__main__':
    with no_ssl_verification():
        """
        Disable SSL verification for simplicity in this example code.
        Do NOT do this in production.
        """

        # Step 1: Request the transmitter config from /.well-known/sse-configuration
        sse_config_response = requests.get(
            url='https://transmitter.most-secure.com/.well-known/sse-configuration',
        )
        sse_config = sse_config_response.json()
        print('example_transmitter_config.json:', json.dumps(sse_config, indent=2))

        # Step 2: Modify the stream config using the configuration_endpoint from step 1
        stream_config_response = requests.post(
            url=sse_config['configuration_endpoint'],
            json={
                'delivery': {
                    'method': 'https://schemas.openid.net/secevent/risc/delivery-method/poll',
                    'endpoint_url': None
                },
                'events_requested': [
                    'https://schemas.openid.net/secevent/risc/event-type/credential-compromise'
                ],
                'format': 'email'
            },
            headers={
                'Authorization': 'Bearer popular-app.com',
            }
        )
        stream_config = stream_config_response.json()
        print("example_stream_config.json:", json.dumps(stream_config, indent=2))

        # Step 3: Add a subject to the stream using the add_subject_endpoint from step 1
        add_subject_response = requests.post(
            url=sse_config['add_subject_endpoint'],
            json={
                'subject': {
                    'format': 'email',
                    'email': 'reginold@popular-app.com'
                }
            },
            headers = {
                'Authorization': 'Bearer popular-app.com',
            }
        )
        print("add_subject_response:", add_subject_response.status_code, add_subject_response.reason)

        # Step 4: Request a verification SET using the verification_endpoint from step 1
        verification_response = requests.post(
            url=sse_config['verification_endpoint'],
            json={
                'state': 'VGhpcyBpcyBhbiBleG'
            },
            headers={
                'Authorization': 'Bearer popular-app.com',
            }
        )
        print("verification_response:", verification_response.status_code, verification_response.reason)

        # Step 5: Get the event from the Transmitter's polling endpoint
        polling_response = requests.post(
            url=stream_config['delivery']['endpoint_url'],
            json={
                "maxEvents": 1,
                "returnImmediately": True
            },
            headers={
                'Authorization': 'Bearer popular-app.com',
            }
        )
        events = polling_response.json()
        print("example_polling_response.json:", json.dumps(events, indent=2))

        # Step 6: Get the JSON Web Key Set (JWKS) for decoding the event
        jwks_uri = sse_config['jwks_uri']
        jwks = requests.get(jwks_uri).json()
        print("example_jwks.json:", json.dumps(jwks, indent=2))

        # Step 7: Decode the SET with pyjwt
        import jwt
        encoded_set = next(iter(events['sets'].values()))
        decoded_set = jwt.decode(
            encoded_set,
            key=jwks['k'],
            algorithms=[jwks['alg']],
            audience='https://popular-app.com'
        )
        print("example_decoded_set.json", json.dumps(decoded_set, indent=2))

        # Step 7: Acknowledge receipt of the event
        jtis_to_ack = list(events['sets'].keys())
        ack_response = requests.post(
            url=stream_config['delivery']['endpoint_url'],
            json={
                "acks": jtis_to_ack,
                "maxEvents": 0,
                "returnImmediately": True,
            },
            headers={
                'Authorization': 'Bearer popular-app.com',
            }
        )
        print("example_polling_response_2.json:", json.dumps(ack_response.json(), indent=2))
