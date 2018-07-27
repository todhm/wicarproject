FROM python:3.6.4

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/requirements.txt

RUN pip install -r requirements.txt

COPY . /usr/src/app

CMD gunicorn -b 0.0.0.0:8000 -w 4 wsgi:app
