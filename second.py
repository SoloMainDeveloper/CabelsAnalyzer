from flask import Blueprint, render_template, session, flash, redirect, url_for, request, make_response
from models import db, Users, Reports
from functools import wraps
import numpy as np
from videoanalyzer import process_video
import bcrypt

second = Blueprint("second", __name__, static_folder="static", template_folder="templates")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("You need to log in first!", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@second.route("/login", methods=["GET", "POST"])
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

@second.route("/logout")
def logout():
    if "user" in session:
        session.pop("user", None)
        session.pop("email", None)
        flash("You have been logged out!", "info")
    return redirect(url_for("login"))

@second.route("/")
@second.route("/home")
@login_required
def home():
    return render_template("index.html")

@second.route("/user", methods=["GET", "POST"])
@login_required
def user():
    email = None
    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = Users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()
            flash("Email was saved")
        else:
            if "email" in session:
                email = session["email"]
        return render_template("user.html", email=email)

@second.route("users/view")
@login_required
def users_view():
    return render_template("users-view.html", values=Users.query.all())

@second.route("reports/view")
@login_required
def reports_view():
    return render_template("reports-list-view.html", values=Reports.query.filter_by(username=session["user"]))

@second.route('/scan', methods=['POST'])
@login_required
def scan():
    if 'file' not in request.files:
        flash('No file. You need to load file')
        return redirect(url_for("second.home"))
    file = request.files['file']
    if file.filename == '':
        flash('Empty filename')
        return redirect(url_for("second.home"))

    frame_interval = int(request.form.get("report_interval"))
    report_name = request.form.get('report_name')
    if file:
        file_content = file.read()
        video_array = np.frombuffer(file_content, np.uint8)
        results = process_video(video_array, frame_interval)

        report = Reports(json_data=results, username=session["user"], report_name=report_name)
        db.session.add(report)
        db.session.commit()

        flash('File uploaded and processed successfully')
        return redirect(url_for("second.home"))
    else:
        flash('Invalid file type')
        return redirect(url_for("second.home"))

@second.route('/reports/view/<report_name>')
@login_required
def view_report(report_name):
    report = Reports.query.filter_by(username=session["user"]).filter_by(report_name=report_name).first()
    if report == None:
        flash("Отчёт с именем='" + report_name + "' не найден")
        return redirect(url_for("second.reports_view"))
    return render_template("report-view.html", report=report)

@second.route('/reports/download/<report_name>')
@login_required
def download_report(report_name):
    report = Reports.query.filter_by(username=session["user"]).filter_by(report_name=report_name).first()
    if report == None:
        flash("Отчёт с именем='" + report_name + "' не найден")
        return redirect(url_for("second.reports_view"))
    response = make_response(render_template("report-view.html", report=report))
    response.headers["Content-Type"] = "text/html"
    response.headers["Content-Disposition"] = f"attachment; filename={report_name}|" + report.created_at.strftime(
        '%Y-%m-%d %H:%M:%S') + ".html"

    return response

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def check_password(hashed_password, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
