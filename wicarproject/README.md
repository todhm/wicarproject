# wicarproject

* This is the project to build webapp platform called Wi-CAR which provide p2p car sharing solution to consumers.
* This project consists of 3 parts main consumer app which provide web app mainly built with Flask and React. Celery worker which hold message queue service and celery beat which sends periodic jobs to celery worker.
* You need to prepare 3 file to fully utilize this web client_secret.json fb_client_secret.json and settings.py to configure secrets of Database, Google App,Facebook App, Bluehouse_App(service to provide sms)
* start Flask app with `python manage.py runserver` in develop mode and  start app with `gunicorn -b localhost:8000 -w 4 wsgi:app  ` in production .
* start celery app with `celery -A celery_worker:celery worker  --loglevel=INFO`
* start celery beat with `celery -A celery_worker:celery beat --loglevel=INFO`
