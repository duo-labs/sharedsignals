FROM python:3.9.6-alpine3.14

WORKDIR /py-openid-sse
COPY . .
RUN pip3 install .

