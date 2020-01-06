FROM nginx:1.17.4-alpine

RUN apk --no-cache add curl
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
