FROM nginx:1.25-alpine

COPY coup.conf /etc/nginx/conf.d/.

RUN mkdir -p /var/www/coup/html
COPY build/. /var/www/coup/html/.
