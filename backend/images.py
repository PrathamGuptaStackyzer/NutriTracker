from ultralytics import YOLO
from imagekitio import ImageKit
from config import *

imagekit = ImageKit(
    private_key=PRIVATE_KEY,
    public_key=PUBLIC_KEY,
    url_endpoint=URL_ENDPOINT,
)

def object_detection(file_path):
    model = YOLO(model=r'D:\Sharad Raval\Working\NutriTracker\best.pt')
    model.predict(file_path, imgsz=640)
    return list(set([val for key, val in model.model.names.items()]))

# temp_file_path = r"C:\Users\Sharad Raval\Downloads\nasi-150_jpg.rf.97500b2f2136112b5e7dd998067efb3b.jpg"
#
# upload_result = imagekit.upload_file(
#     file=open(temp_file_path, "rb"),
#     file_name=temp_file_path,
#     options=UploadFileRequestOptions(use_unique_file_name=True, tags=['backend-upload'])
# )
#
# file_url = upload_result.url
# if upload_result.response_metadata.http_status_code == 200:
#     print(upload_result.response_metadata.http_status_code)
# print(upload_result.response_metadata.http_status_code)
