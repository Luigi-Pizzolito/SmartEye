import os
import cv2
import numpy as np
import multiprocessing

# *******************************************************************
# * Author: 2024 Kael (956136864@qq.com)
# *         2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
# *******************************************************************
import time
import requests
import json

# Import Kafka connection
from kafkacon import KafkaCon

# -- import Computer Vision module
from VideoProcess.KafkaFace import FaceRecognizer, KafkaFace
from VideoProcess.KafkaHand import GestureDetection, KafkaHand
from VideoProcess.KafkaPose import FallDetection, KafkaPose


def FaceProcess():
    print("Starting face recognition for", os.environ["IN_TOPIC"])
    # start Kafka client
    kafka_con = KafkaCon(
        bootstrap_servers=os.environ["KAFKA_SERVERS"],
        mjpeg_host=os.environ["MJPEG_SERVER"]
    )
    kafka_con.connect()

    # define topics
    in_topic = os.environ["IN_TOPIC"]
    out_topic = os.environ["OUT_TOPIC_FACE"]
    data_topic = os.environ["DATA_TOPIC_FACE"]

    # read frames with CV
    esp_cam = cv2.VideoCapture(kafka_con.get_stream(in_topic))

    KafkaFace(esp_cam, kafka_con, out_topic, data_topic)

    # close Kafka connection when program exits
    kafka_con.close()


def PoseProcess():
    print("Starting pose recognition for", os.environ["IN_TOPIC"])
    # start Kafka client
    kafka_con = KafkaCon(
        bootstrap_servers=os.environ["KAFKA_SERVERS"],
        mjpeg_host=os.environ["MJPEG_SERVER"]
    )
    kafka_con.connect()

    # define topics
    in_topic = os.environ["IN_TOPIC"]
    out_topic = os.environ["OUT_TOPIC_POSE"]
    data_topic = os.environ["DATA_TOPIC_POSE"]

    # read frames with CV
    esp_cam = cv2.VideoCapture(kafka_con.get_stream(in_topic))

    KafkaPose(esp_cam, kafka_con, out_topic, data_topic)

    # close Kafka connection when program exits
    kafka_con.close()


def HandProcess():
    print("Starting gesture recognition for", os.environ["IN_TOPIC"])
    # start Kafka client
    kafka_con = KafkaCon(
        bootstrap_servers=os.environ["KAFKA_SERVERS"],
        mjpeg_host=os.environ["MJPEG_SERVER"]
    )
    kafka_con.connect()

    # define topics
    in_topic = os.environ["IN_TOPIC"]
    out_topic = os.environ["OUT_TOPIC_GESTURE"]
    data_topic = os.environ["DATA_TOPIC_GESTURE"]

    # read frames with CV
    esp_cam = cv2.VideoCapture(kafka_con.get_stream(in_topic))

    KafkaHand(esp_cam, kafka_con, out_topic, data_topic)

    # close Kafka connection when program exits
    kafka_con.close()


def CameraStreamReady():
    try:
        mjpeg_host=os.environ["MJPEG_SERVER"]
        target_stream = os.environ["IN_TOPIC"]
        response = requests.get('http://'+mjpeg_host + '/list')
        data = response.json()
        streams = data.get('Streams', [])
        for stream in streams:
            if target_stream in stream:
                return True
    except Exception as e:
        print("An error occurred:", e)
    return False


def main():
    print("started main")
    # --
    # face_process = multiprocessing.Process(target=FaceProcess, args=())
    # face_process.start()
    # pose_process = multiprocessing.Process(target=PoseProcess, args=())
    # pose_process.start()
    hand_process = multiprocessing.Process(target=HandProcess, args=())
    hand_process.start()
    #  multiple process --


if __name__ == "__main__":
    target_stream = os.environ["IN_TOPIC"]
    print("starting AI proccess")
    while True:
        print("Waiting for", target_stream, "stream...")
        if CameraStreamReady():
            print("Starting AI Processing on", target_stream)
            time.sleep(5)
            main()
            while True:
                time.sleep(1)
        time.sleep(1)
