from celery import Celery

def make_celery(flask_app):
    # Create Celery app with NO old-style config
    celery = Celery(flask_app.import_name)

    # Use new-style (lowercase) config keys
    celery.conf.update(
        broker_url=flask_app.config["CELERY_BROKER_URL"],
        result_backend=flask_app.config["CELERY_RESULT_BACKEND"],
    )

    # Make tasks run inside Flask app context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return super().__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery
