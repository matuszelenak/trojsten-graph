FROM python:3.7-alpine

ENV PYTHONUNBUFFERED=0

ENV DJANGO_SETTINGS_MODULE=graph.settings.production

RUN apk add --no-cache --virtual build-deps curl gcc g++ make postgresql-dev bash

RUN mkdir /graph

WORKDIR /graph

ADD . /graph

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

COPY ./deployment.sh /usr/local/bin/deployment.sh

RUN chmod 777 /usr/local/bin/deployment.sh

CMD /usr/local/bin/deployment.sh
