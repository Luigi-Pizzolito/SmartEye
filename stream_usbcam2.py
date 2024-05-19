import cv2
from flask import Flask, Response

app = Flask(__name__)

def webcam_stream():
    cap = cv2.VideoCapture(2)  # Use the first webcam (index 0)
    # cap.set(cv2.CAP_PROP_FPS, 5)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize the frame to VGA resolution (640x480)
        # rframe = cv2.resize(frame, (320, 240))
        rframe = cv2.resize(frame, (640, 480))

        rframe = auto_adjust_brightness_contrast(rframe)

        # Convert the frame to JPEG format
        ret, jpeg = cv2.imencode('.jpg', rframe)
        if not ret:
            break

        # Yield the JPEG frame
        yield (b'--123456789000000000000987654321\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

    cap.release()

def auto_adjust_brightness_contrast(image):
    # Convert image to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    
    # Split channels
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to the L channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_equalized = clahe.apply(l)
    
    # Merge channels
    lab_equalized = cv2.merge((l_equalized, a, b))
    
    # Convert back to BGR color space
    equalized_image = cv2.cvtColor(lab_equalized, cv2.COLOR_LAB2BGR)
    
    return equalized_image
    


@app.route('/')
def video_feed():
    # Return the response generated from the webcam_stream generator function
    return Response(webcam_stream(), mimetype='multipart/x-mixed-replace; boundary=123456789000000000000987654321')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

