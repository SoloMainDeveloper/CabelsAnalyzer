import cv2
import tempfile
import os
import io
from inference_sdk import InferenceHTTPClient
from PIL import Image
from config import API_KEY
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

def process_frame(client, image, count, fps):
    image_bytes = cv2.imencode('.jpg', image)[1].tobytes()
    image = Image.open(io.BytesIO(image_bytes))
    logging.info(f"Кадр {count} начало")
    result = client.run_workflow(
        workspace_name="cabelsanalyzer",
        workflow_id="detect-count-and-visualize",
        images={"image": image},
        use_cache=True
    )[0]

    result["frame_time"] = seconds_to_hhmmss(round(count / fps))
    logging.info(f"Кадр {result['frame_time']} - {count} конец")
    return result


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
        api_url="http://localhost:9001/",
        api_key=API_KEY
    )
    logging.info(f"Начало видео. {frame_count_interval}.")

    with ThreadPoolExecutor() as executor:
        futures = []

        while True:
            success, image = vidcap.read()
            if not success:
                break

            if count % frame_count_interval == 0:
                futures.append(executor.submit(process_frame, client, image, count, fps))
            count += 1

        for future in as_completed(futures):
            results.append(future.result())

    vidcap.release()
    os.remove(temp_video_path)
    logging.info("Конец анализа видео")

    sorted_results = sorted(results, key=lambda x: time_to_seconds(x["frame_time"]))
    return sorted_results

def seconds_to_hhmmss(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def time_to_seconds(frame_time):
    h, m, s = map(int, frame_time.split(':'))
    return h * 3600 + m * 60 + s
