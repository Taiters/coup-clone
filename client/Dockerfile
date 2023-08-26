FROM node:18 as build

RUN mkdir /usr/coup
WORKDIR /usr/coup

COPY package.json /usr/coup/.
COPY package-lock.json /usr/coup/.
RUN npm install

COPY . /usr/coup
RUN npm run build

FROM nginx:1.25-alpine

RUN mkdir -p /var/www/coup/html
COPY coup.conf /etc/nginx/conf.d/.
COPY --from=build /usr/coup/build/. /var/www/coup/html/.
