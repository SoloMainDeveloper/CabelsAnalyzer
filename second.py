from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from models import db, Users, Reports
from functools import wraps
import numpy as np
import cv2
import tempfile
import os
import io
from inference_sdk import InferenceHTTPClient
from PIL import Image
from config import API_KEY


second = Blueprint("second", __name__, static_folder="static", template_folder="templates")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("You need to log in first!", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@second.route("/admin")
@login_required
def home():
    return "This is an admin route that requires login."

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
    return render_template("reports-view.html", values=Reports.query.filter_by(username=session["user"]))

@second.route('/scan', methods=['POST'])
@login_required
def scan():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    frame_interval = int(request.form.get('frame_interval', 1))
    if file and file.filename.endswith('.MOV'):
        file_content = file.read()
        video_array = np.frombuffer(file_content, np.uint8)
        results = process_video(video_array, frame_interval)

        report = Reports(json_data=results, username=session["user"])
        db.session.add(report)
        db.session.commit()

        flash('File uploaded and processed successfully')
        return redirect(url_for("home"))
    else:
        flash('Invalid file type')
        return redirect(url_for("home"))


def process_video(video_array, frame_interval):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
        temp_file.write(video_array)
        temp_video_path = temp_file.name

    vidcap = cv2.VideoCapture(temp_video_path)

    results = []
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_count_interval = int(fps * frame_interval)

    count = 0
    client = InferenceHTTPClient(
        api_url="https://detect.roboflow.com",
        api_key=API_KEY
    )

    while True:
        success, image = vidcap.read()
        if not success:
            break

        if count % frame_count_interval == 0:
            image_bytes = cv2.imencode('.jpg', image)[1].tobytes()
            image = Image.open(io.BytesIO(image_bytes))
            results.append(client.run_workflow(
                workspace_name="cabelsanalyzer",
                workflow_id="detect-count-and-visualize",
                images={
                    "image": image
                },
                use_cache=True
            )[0])
        count += 1

    vidcap.release()
    os.remove(temp_video_path)
    return results
