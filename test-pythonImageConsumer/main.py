import cv2
import numpy as np

# Import Kafka connection
from kafkacon import KafkaCon

# Example usage:
def main():
    # start Kafka client
    kafka_con = KafkaCon(
        bootstrap_servers='kafka:9092',
        mjpeg_host='mjpegstreamer:8095'
    )
    kafka_con.connect()

    # define topics
    in_topic = "camera0"
    out_topic = "faces-camera0-stream"
    data_topic = "faces-camera0"

    # read frames with CV
    cv2.VideoCapture(kafka_con.get_stream(in_topic))

    # send frames
    # -- empty image
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    kafka_con.send_frame(out_topic, frame)

    # send data
    faces = ["person1", "person2"]
    kafka_con.send_data(data_topic, faces)

    # close Kafka connection when program exits
    kafka_con.close()