import cv2
import io
from io import BytesIO
import base64
from inference_sdk import InferenceHTTPClient
from PIL import Image
import os
import glob
import json
import requests
import supervision as sv
from PIL.ImageFile import ImageFile
#from config import API_KEY

# Подготовка данных (разделение видео на кадры)
def extract_frames(video_path):
    vidcap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        success, image = vidcap.read()
        if not success:
            break
        frames.append(image)
    return frames;


image_path = "C:\\Users\\solom\\Downloads\\1.MOV"
frames = extract_frames(image_path)

if frames:
    for i in range(len(frames)):
        # Выводим первый кадр на экран
        cv2.imshow('Frame', frames[i])  # Здесь можно указать индекс нужного кадра

        # Ожидаем нажатия клавиши
        cv2.waitKey(0)  # 0 означает, что программа будет ждать бесконечно, пока не будет нажата клавиша

        # Закрываем все окна
        cv2.destroyAllWindows()
else:
    print("Не удалось извлечь кадры из видео.")
print(frames)
# with open(image_path, "rb") as image_file:
#     image_bytes = image_file.read()
# image = Image.open(io.BytesIO(image_bytes))
#
# client = InferenceHTTPClient(
#     api_url="https://detect.roboflow.com",
#     api_key="9gobrtw7bAnhMrmIZspP"
# )
#
# result = client.run_workflow(
#     workspace_name="cabelsanalyzer",
#     workflow_id="detect-count-and-visualize",
#     images={
#         "image": image
#     },
#     use_cache=True # cache workflow definition for 15 minutes
# )[0]
#
# image_bytes = base64.b64decode(result["output_image"])
#
# # Создание изображения из байтов
# img = Image.open(BytesIO(image_bytes))
#
# # Отображение изображения
# img.show()
#
# print(result)