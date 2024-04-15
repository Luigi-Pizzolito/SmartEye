from flask import Flask, render_template, Response,request
import cv2
import subprocess
from Face_recognition.face_recogition import process_face
from Face_recognition.Face_read import process_faceRead
from Pose_estimation.gesture_recognition.HandClassification import process_gesture
from Pose_estimation.Fall_detection.fall_detection import process_fall
import threading

app = Flask(__name__,template_folder='templates',static_folder='static')

@app.route('/video_feed1')
def video_feed1():
    #Video streaming route. Put this in the src attribute of an img tag
    cap_face = cv2.VideoCapture(0)
    return Response(process_face(cap_face), mimetype='multipart/x-mixed-replace; boundary=frame')
    return ""
# @app.route('/video_feed2')
# def video_feed2():
#     cap_fall = cv2.VideoCapture("1.mp4")
#     #Video streaming route. Put this in the src attribute of an img tag
#     return Response(process_fall(cap_fall), mimetype='multipart/x-mixed-replace; boundary=frame')
#     return ""
# @app.route('/video_feed3')
# def video_feed3():
#     cap_gest = cv2.VideoCapture("2.mp4")
#     #Video streaming route. Put this in the src attribute of an img tag
#     return Response(process_gesture(cap_gest), mimetype='multipart/x-mixed-replace; boundary=frame')
#     return ""

# @app.route('/video_feed4')
# def video_feed4():
#     cap_face1 = cv2.VideoCapture(0)
#     #Video streaming route. Put this in the src attribute of an img tag
#     return Response(process(cap_face1), mimetype='multipart/x-mixed-replace; boundary=frame')
#     return ""

# @app.route('/trigger_event')
# def trigger_event():
#     # 在这里处理触发的事件，例如修改 k 的值为 ord('n')
#     return 'Event triggered successfully'


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)