import os
import sys
import cv2
import numpy as np
import multiprocessing

# *******************************************************************
# * Author: 2024 Kael (956136864@qq.com)
# *         2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
#
# * LastEdit: 2024/04/23 Kael (956136864@qq.com)
# * Commit: error respond and report
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
    
def DetectionProcess(process, handle):
    print("Starting face recognition for", os.environ["IN_TOPIC"])
    # start Kafka client
    kafka_con = KafkaCon(
        bootstrap_servers=os.environ["KAFKA_SERVERS"],
        mjpeg_host=os.environ["MJPEG_SERVER"]
    )
    kafka_con.connect()

    # define topics
    in_topic = os.environ["IN_TOPIC"]
    out_topic = os.environ["OUT_TOPIC_" + handle ]
    data_topic = os.environ["DATA_TOPIC_" + handle ]
    
    try:
    # read frames with CV
        esp_cam = cv2.VideoCapture(kafka_con.get_stream(in_topic))       
        process(esp_cam, kafka_con, out_topic, data_topic )
    except Exception as e:
        # kafka_con.send_data(data_topic, [f"Error(s) raised in {handle } Process with exception {e }." ] )
        raise Exception(f"Error(s) raised in {handle } Process with exception {e }." )
    
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
    # -- multiple process
    processes = []
    process = multiprocessing.Process(target=DetectionProcess, \
        name="face_process", args=(KafkaFace, "FACE") )
    process.start()
    processes.append(process )
    process = multiprocessing.Process(target=DetectionProcess, \
        name="pose_process", args=(KafkaPose, "POSE") )
    process.start()
    processes.append(process )
    process = multiprocessing.Process(target=DetectionProcess, \
        name="hand_process", args=(KafkaHand, "GESTURE") )
    process.start()
    processes.append(process )
    #  multiple process --
    
    # -- error respond and report
    are_u_alive =  lambda x: x.is_alive()
    while True:
        if all(list(map(are_u_alive, processes ) ) ):
            time.sleep(1)
            
            
        else:
            for process in processes:
                process.terminate()
                
            for process in processes:
                process.join()   
                
            sys.exit() 
    # error respond and report --
    


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