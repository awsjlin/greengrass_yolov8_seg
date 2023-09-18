import sys, traceback
import datetime
import cv2
import json
import torch
import onnxruntime as rt
import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    PublishToIoTCoreRequest,
    JsonMessage,
    QOS
)
import argparse
from YOLOSeg import YOLOSeg
from utils import class_names


# Initialize the webcam
cap = cv2.VideoCapture(0)

parser = argparse.ArgumentParser(description='finds model')
parser.add_argument('--model', help='trained model')
args = parser.parse_args()

MODEL_PATH = args.model
#print("\n\n************Model Path: ", MODEL_PATH)

# Initialize YOLOv5 Instance Segmentator
#model = "yolov8n-seg.onnx"
yoloseg = YOLOSeg(MODEL_PATH, conf_thres=0.3, iou_thres=0.3)


# Create the AWS IoT Greengrass Core IPC Client
TIMEOUT = 10
topic = "objDetect/topic"
qos = QOS.AT_LEAST_ONCE
ipc_client = awsiot.greengrasscoreipc.connect()  

cv2.namedWindow("ObjDetection & Segmentation", cv2.WINDOW_NORMAL)
while cap.isOpened():

    # Read frame from the video
    ret, frame = cap.read()

    if not ret:
        break

    # Update object localizer
    boxes, scores, class_ids, masks = yoloseg(frame)
    obj = []
    #print("Boxes: ", boxes, " Scores: ", scores, " Class IDs: ", class_ids)

    # Organize the data per object
    if len(class_ids) > 0:
        for index, item in enumerate(class_ids):
            #print(index, item)
            obj.append({'id':class_names[item], 'score':float(scores[index]), 'box':boxes[index].tolist(), 'timestamp' : str(datetime.datetime.now())})

        # Prepare JSON for data IPC publish
        obj_json = json.dumps(obj)
        print(obj_json)

        request = PublishToIoTCoreRequest()
        request.topic_name = topic
        request.payload = bytes(obj_json, "utf-8")
        request.qos = qos
        operation = ipc_client.new_publish_to_iot_core()
        operation.activate(request)
        future_response = operation.get_response()
        future_response.result(TIMEOUT)
    else:
        obj = None

    combined_img = yoloseg.draw_masks(frame)
    cv2.imshow("ObjDetection & Segmentation", combined_img)


    #cv2.imwrite("image.jpg", combined_img)

    # Press key q to stop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
