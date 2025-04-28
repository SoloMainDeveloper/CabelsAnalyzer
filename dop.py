from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from second import second
from models import db, Users

app = Flask(__name__)
app.register_blueprint(second, url_prefix="")
app.secret_key = "absolutely_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=60)

db.init_app(app)

@app.route("/home")
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user

        found_user = Users.query.filter_by(name=user).first()
        if found_user:
            session["email"] = found_user.email
        else:
            usr = Users(user, None)
            db.session.add(usr)
            db.session.commit()

        flash("Login successfully!")
        return redirect(url_for("second.user"))
    else:
        if "user" in session:
            flash("Already logged in!")
            return redirect(url_for("second.user"))
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