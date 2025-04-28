from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from models import db, Users

second = Blueprint("second", __name__, static_folder="static", template_folder="templates")

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("You need to log in first!", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@second.route("/admin")
#@login_required
def home():
    return "This is an admin route that requires login."

@login_required
@second.route("/user", methods=["GET", "POST"])
def user():
    return "Users"
    # email = None
    # if "user" in session:
    #     user = session["user"]
    #
    #     if request.method == "POST":
    #         email = request.form["email"]
    #         session["email"] = email
    #         found_user = Users.query.filter_by(name=user).first()
    #         found_user.email = email
    #         db.session.commit()
    #         flash("Email was saved")
    #     else:
    #         if "email" in session:
    #             email = session["email"]
    #     return render_template("user.html", email="dog")

# @second.route("/view")
# @login_required
# def view():
#     return render_template("view.html", values=Users.query.all())
#