FROM python:3.11-alpine

RUN mkdir /usr/coup
WORKDIR /usr/coup

COPY . /usr/coup
RUN pip install -r requirements.txt

CMD python app.py