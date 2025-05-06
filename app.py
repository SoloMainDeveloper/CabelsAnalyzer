from flask import Flask
from celery import Celery
from models import db, Users, Reports
from second import second

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    return celery


def create_app():
    app = Flask(__name__)
    app.secret_key = "absolutely_secret_key"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

    db.init_app(app)

    app.register_blueprint(second, url_prefix="")

    return app


app = create_app()
celery = make_celery(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)