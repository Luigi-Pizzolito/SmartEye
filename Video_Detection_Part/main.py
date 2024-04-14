from flask import Flask, render_template, Response
import cv2
from Face_recognition.face_recogition import process_face
from Pose_estimation.gesture_recognition.HandClassification import process_gesture
from Pose_estimation.Fall_detection.fall_detection import process_fall
import threading
import json
import os

app = Flask(__name__)


@app.route('/'+os.environ["CAMERA"]+'-face.mjpeg')
def face_feed():

    #Video streaming route. Put this in the src attribute of an img tag
    cap_face = cv2.VideoCapture('http://'+os.environ["MJPEG_SERVER"]+'/'+os.environ["CAMERA"]+'-stream.mjpeg')
    return Response(process_face(cap_face), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/'+os.environ["CAMERA"]+'-pose.mjpeg')
def fall_feed():
    cap_fall = cv2.VideoCapture('http://'+os.environ["MJPEG_SERVER"]+'/'+os.environ["CAMERA"]+'-stream.mjpeg')
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(process_fall(cap_fall), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/'+os.environ["CAMERA"]+'-gest.mjpeg')
def gest_feed():
    cap_gest = cv2.VideoCapture('http://'+os.environ["MJPEG_SERVER"]+'/'+os.environ["CAMERA"]+'-stream.mjpeg')
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(process_gesture(cap_gest), mimetype='multipart/x-mixed-replace; boundary=frame')


# ? on index open /, list all endpoints
# Define a function to get a list of endpoints
def get_endpoints():
    endpoints = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            endpoints.append({
                'endpoint': rule.endpoint,
                'methods': sorted(rule.methods),
                'path': str(rule)
            })
    return endpoints

# Define a route to handle root path and provide list of endpoints
@app.route('/')
def root():
    endpoints = get_endpoints()
    json_string = json.dumps(endpoints, separators=(',', ':'))
    return json_string


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ["PORT"], debug=True)