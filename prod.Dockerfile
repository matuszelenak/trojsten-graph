FROM python:alpine3.16 as builder

WORKDIR /usr/src/graph

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip

COPY ./requirements.txt /usr/src/graph/requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/graph/wheels -r requirements.txt


FROM python:alpine3.16

RUN mkdir -p /home/graph

RUN addgroup -S graph && adduser -S graph -G graph

ENV PYTHONUNBUFFERED 1
ENV HOME=/home/graph
ENV APP_HOME=/home/graph/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

RUN apk update && apk add libpq bash
COPY --from=builder /usr/src/graph/wheels /wheels
COPY --from=builder /usr/src/graph/requirements.txt .
RUN pip install --no-cache /wheels/*

COPY /graph .
RUN chown -R graph:graph $APP_HOME

USER graph
