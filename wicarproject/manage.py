import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
import coverage
from flask_script import Manager, Server
from flask_migrate import MigrateCommand

from flask import session
from application import create_app,create_admin_app
from celery.bin.celery import main as celery_main
from celery import current_app,group,chain


app = create_app()
admin_app = create_admin_app()
manager = Manager(app)

COV = coverage.coverage(
    branch=True,
    include='./*',
    omit=[
    'settings.py',
    'wsgi.py',
    'tests.py',
    'venv/*',
    'static/*',
    'templates/*'
    ]
)
COV.start()

#Turn on debugger by default and reloader
manager.add_command('db', MigrateCommand)

manager.add_command("runserver", Server(
    use_debugger = False,
    use_reloader = True,
    threaded=True,
    host = os.getenv('IP', '0.0.0.0'),
    port = int(os.getenv('PORT', 5000)))
)

@manager.command
def test():
    tests = unittest.TestLoader().discover('./', pattern='tests.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('./',pattern='tests.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.html_report()
        COV.erase()
        return 0
    return 1


if __name__ == "__main__":
    manager.run()
