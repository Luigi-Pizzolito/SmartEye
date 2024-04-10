import os
import cv2
import numpy as np
import multiprocessing

# Import Kafka connection
from kafkacon import KafkaCon

# -- import Computer Vision module
from KafkaVideoProcess.KafkaFace import FaceRecognizer, KafkaFace
from KafkaVideoProcess.KafkaHand import GestureDetection, KafkaHand
from KafkaVideoProcess.KafkaPose import FallDetection, KafkaPose

def FaceProcess():
    # start Kafka client
    kafka_con = KafkaCon(
        bootstrap_servers = os.environ[KAFKA_SERVERS],
        mjpeg_host=os.environ[MJPEG_SERVER]
    )
    kafka_con.connect()

    # define topics
    in_topic = os.environ[IN_TOPIC]
    out_topic = os.environ[OUT_TOPIC]
    data_topic = os.environ[DATA_TOPIC]

    # read frames with CV
    esp_cam = cv2.VideoCapture(kafka_con.get_stream(in_topic))
    
    KafkaFace(esp_cam, kafka_con, out_topic, data_topic )
    
    # close Kafka connection when program exits
    kafka_con.close()
    
    
    
def PoseProcess():
    # start Kafka client
    kafka_con = KafkaCon(
        bootstrap_servers = os.environ[KAFKA_SERVERS],
        mjpeg_host=os.environ[MJPEG_SERVER]
    )
    kafka_con.connect()

    # define topics
    in_topic = os.environ[IN_TOPIC]
    out_topic = os.environ[OUT_TOPIC]
    data_topic = os.environ[DATA_TOPIC]


    # read frames with CV
    esp_cam = cv2.VideoCapture(kafka_con.get_stream(in_topic))
    
    KafkaPose(esp_cam, kafka_con, out_topic, data_topic )
    
    # close Kafka connection when program exits
    kafka_con.close()
    
    
    
def HandProcess():
    # start Kafka client
    kafka_con = KafkaCon(
        bootstrap_servers = os.environ[KAFKA_SERVERS],
        mjpeg_host=os.environ[MJPEG_SERVER]
    )
    kafka_con.connect()

    # define topics
    in_topic = os.environ[IN_TOPIC]
    out_topic = os.environ[OUT_TOPIC]
    data_topic = os.environ[DATA_TOPIC]


    # read frames with CV
    esp_cam = cv2.VideoCapture(kafka_con.get_stream(in_topic))
    
    KafkaHand(esp_cam, kafka_con, out_topic, data_topic )
    
    # close Kafka connection when program exits
    kafka_con.close()
    



def main():
    # --
    face_process = multiprocessing.Process(target=FaceProcess, args=() )
    face_process.start()
    pose_process = multiprocessing.Process(target=PoseProcess, args=() )
    pose_process.start()
    hand_process = multiprocessing.Process(target=HandProcess, args=() )
    hand_process.start()
    #  multiple process --
    


if __name__ == "__main__":
    main()