FROM python:3.8.0-alpine as builder

# set work directory
WORKDIR /usr/src/graph

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache --virtual build-deps curl gcc g++ make postgresql-dev postgresql-client bash

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/graph/wheels -r requirements.txt

FROM python:3.8.0-alpine

RUN mkdir -p /home/graph

RUN addgroup -S graph && adduser -S graph -G graph

ENV HOME=/home/graph
ENV GRAPH_HOME=/home/graph/web
RUN mkdir $GRAPH_HOME
WORKDIR $GRAPH_HOME

RUN apk update && apk add libpq
COPY --from=builder /usr/src/graph/wheels /wheels
COPY --from=builder /usr/src/graph/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

COPY ./entrypoint.prod.sh $GRAPH_HOME

COPY . $GRAPH_HOME

RUN chown -R graph:graph $GRAPH_HOME

USER graph

ENTRYPOINT ["/home/graph/web/entrypoint.prod.sh"]
