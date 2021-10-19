FROM python:3.9

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Where our private key, public key, a JWKS file are stored
ENV KEY_PATH="/usr/src/app/keys"

# The key ID of the JSON Web Key Set that is currently in use
ENV KEY_ID="transmitter-EC256-001"

COPY requirements.txt /usr/src/app/
COPY test-requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir -r test-requirements.txt

# Idempotently create a private key, public key, and JWKS file
RUN python make_keys.py $KEY_PATH $KEY_ID

EXPOSE 443

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]
