from flask import Flask, render_template, Response
import cv2
from Face_recognition.face_recogition import process_face
from Pose_estimation.gesture_recognition.HandClassification import process_gesture
from Pose_estimation.Fall_detection.Fall_detection import process_fall

app = Flask(__name__,template_folder='templates')


cap_gest=cv2.VideoCapture(0)
cap_fall=cv2.VideoCapture('1.mp4')
cap_face=cv2.VideoCapture('2.mp4')



@app.route('/video_fee1')
def video_feed1():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(process_face(cap_face), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/video_feed2')
def video_fee2():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(process_fall(cap_fall), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/video_fee3')
def video_feed3():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(process_gesture(cap_gest), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)