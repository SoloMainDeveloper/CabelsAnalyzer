import cv2
import tempfile
import os
import io
from inference_sdk import InferenceHTTPClient
from PIL import Image
from config import API_KEY

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
            result = (client.run_workflow(
                workspace_name="cabelsanalyzer",
                workflow_id="detect-count-and-visualize",
                images={
                    "image": image
                },
                use_cache=True
            )[0])
            result["frame_time"] = seconds_to_hhmmss(round(count / fps))
            results.append(result)
        count += 1

    vidcap.release()
    os.remove(temp_video_path)
    return results

def seconds_to_hhmmss(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"
