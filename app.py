from flask import Flask, request, redirect, render_template, url_for, session, flash
from celery import Celery
from models import db, Users, Reports
from second import second
import bcrypt

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

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def check_password(hashed_password, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["login"]
        password = request.form["password"]

        found_user = Users.query.filter_by(name=user).first()
        if not found_user:
            hashed_password = hash_password(password)
            usr = Users(name=user, password=hashed_password)
            db.session.add(usr)
            db.session.commit()
            session["user"] = user
            flash("Аккаунт создан. Добро пожаловать, " + user)
            return redirect(url_for("second.home"))
        else:
            if check_password(found_user.password, password):
                session["user"] = user
                flash("Login successfully!")
                return redirect(url_for("second.home"))
            else:
                flash("Пароль неверный.")
                return redirect(url_for("login"))
    else:
        if "user" in session:
            flash("Already logged in!")
            return redirect(url_for("second.home"))
        return render_template("login.html")

@app.route("/logout")
def logout():
    if "user" in session:
        session.pop("user", None)
        session.pop("email", None)
        flash("You have been logged out!", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)