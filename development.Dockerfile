FROM python:alpine3.16

WORKDIR /usr/src/graph

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add supervisor postgresql-dev libpq gcc python3-dev musl-dev bash
RUN pip install --upgrade pip

COPY ./requirements.txt /usr/src/graph/requirements.txt
RUN pip install -r requirements.txt


RUN mkdir -p /home/graph
# RUN addgroup -S capila && adduser -S capila -G capila

ENV APP_HOME=/home/graph/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

ADD /graph .