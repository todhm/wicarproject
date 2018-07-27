from celery import Celery
from celery.schedules import crontab
from application import create_app
from carbooking.tasks import cancel_overtime_booking, change_past_booking,finish_past_booking_celery
from caruser.tasks import get_best_cars_celery


def create_celery(app):
    celery = Celery(app.import_name,
                    backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

flask_app = create_app()
celery = create_celery(flask_app)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Executes every hour
    sender.add_periodic_task(
        crontab(minute='0',hour='*'),
        cancel_overtime_booking.s(),
        name="cancel booking"
    )
    sender.add_periodic_task(
            crontab(minute='1',hour='*'),
            finish_past_booking_celery.s(),
            name="finish booking"
        )
    sender.add_periodic_task(
        crontab(minute='0',hour='9'),
        get_best_cars_celery.s(),
        name="update best car for index page"
    )
