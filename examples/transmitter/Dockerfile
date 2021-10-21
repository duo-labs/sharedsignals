FROM python:3.9

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 443

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]
