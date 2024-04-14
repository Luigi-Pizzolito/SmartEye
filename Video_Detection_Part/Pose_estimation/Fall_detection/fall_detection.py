# ********************************************************************
#   * Author: 2024 Jingdi Lei (@https://github.com/kyrieLei)
# ********************************************************************


import cv2
import mediapipe as mp
import numpy as np




class FallDetection:
    def __init__(self):
        self.counter = 0
        self.stage = None

        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils

    def calculate_angle(self,a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def give_angle(self,results):
        landmarks = results.pose_landmarks.landmark

        left_ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        left_knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
        nose = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]

        right_ankle = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
        right_knee = [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        right_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]

        angle = self.calculate_angle(left_hip, left_knee, left_ankle)
        angle_2 = self.calculate_angle(right_hip, right_knee, right_ankle)

        return angle, angle_2
def process_fall(cap):
    fall_detector=FallDetection()
    with fall_detector.mp_pose.Pose(
            min_detection_confidence=0.7, min_tracking_confidence=0.7
    ) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                angle, angle_2 = fall_detector.give_angle(results)
                if angle > 160 and angle_2 > 160:
                    fall_detector.stage = "up"
                if (angle < 100 or angle_2 < 100):
                    fall_detector.stage = "fall"
                    fall_detector.counter = 1
                    print(angle)
            except:
                pass

            cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)

            cv2.putText(image, 'Fall', (15, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, str(fall_detector.counter),
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.putText(image, 'Stage', (120, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, fall_detector.stage,
                        (120, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

            fall_detector.mp_drawing.draw_landmarks(image, results.pose_landmarks, fall_detector.mp_pose.POSE_CONNECTIONS,
                                      fall_detector.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                      fall_detector.mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                      )

            # cv2.imshow('Camera', image)
            ret, buffer = cv2.imencode('.jpg', image)
            image = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')

            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
