###########
# BUILDER #
###########

# pull official base image
FROM python:3.9.6-alpine as builder

# set work directory
WORKDIR /usr/src/graph

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip

# install dependencies
COPY ./requirements.txt /usr/src/graph/requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/graph/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM python:3.9.6-alpine

# create directory for the app user
RUN mkdir -p /home/graph

# create the app user
RUN addgroup -S graph && adduser -S graph -G graph

# create the appropriate directories
ENV HOME=/home/graph
ENV APP_HOME=/home/graph/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# install dependencies
RUN apk update && apk add libpq
COPY --from=builder /usr/src/graph/wheels /wheels
COPY --from=builder /usr/src/graph/requirements.txt .
RUN pip install --no-cache /wheels/*

# copy project
COPY /graph $APP_HOME

# chown all the files to the app user
RUN chown -R graph:graph $APP_HOME

# change to the app user
USER graph
