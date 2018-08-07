import os
from flask import Flask
from flaskext.markdown import Markdown
from flask_bootstrap import Bootstrap
from flask_mongoengine import MongoEngine
from flask_celery import Celery
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
import logging
from utilities.flask_tracking import Tracking


db = SQLAlchemy()
mdb = MongoEngine()
migrate = Migrate()
csrf = CSRFProtect()
celery= Celery()

# images
uploaded_images = UploadSet('images', IMAGES)

def create_app(**config_overrides):
    app = Flask("wicar")
    Bootstrap(app)
    Markdown(app)
    CORS(app)

    #Update settings from settings.py
    app.config.from_pyfile('settings.py')
    #If other settings came it update that settings.
    app.config.update(config_overrides)

    configure_uploads(app, uploaded_images)

    db.init_app(app)
    from caruser import models
    from carupload import models
    from carbooking import models
    migrate.init_app(app,db)
    mdb.init_app(app)
    celery.init_app(app)

    from errors.views import error_app
    from caruser.views import carshare_app
    from carupload.views import carupload_app
    from carbooking.views import carbooking_app
    from carterms.views import carterms_app
    from carapi.carupload_api import carupload_api_app
    from carapi.carbooking_api import carbooking_api_app
    from carapi.userinfo_api import userinfo_api_app
    app.register_blueprint(error_app)
    app.register_blueprint(carshare_app)
    app.register_blueprint(carupload_app)
    app.register_blueprint(carbooking_app)
    app.register_blueprint(carupload_api_app)
    app.register_blueprint(carbooking_api_app)
    app.register_blueprint(userinfo_api_app)
    app.register_blueprint(carterms_app)
    csrf.init_app(app)
    csrf.exempt(carupload_api_app)
    csrf.exempt(carbooking_api_app)
    csrf.exempt(userinfo_api_app)

    Tracking(app)

    return app


def create_admin_app(**config_overrides):
    app = Flask("wicar_admin_app")
    Bootstrap(app)
    Markdown(app)
    CORS(app)

    #Update settings from settings.py
    app.config.from_pyfile('settings.py')
    #If other settings came it update that settings.
    app.config.update(config_overrides)

    configure_uploads(app, uploaded_images)
    from caruser import models
    from carupload import models
    from carbooking import models
    db.init_app(app)
    migrate.init_app(app,db)
    mdb.init_app(app)
    celery.init_app(app)

    from wicaradmin.views import wicar_admin_app
    app.register_blueprint(wicar_admin_app)


    Tracking(app)

    return app
