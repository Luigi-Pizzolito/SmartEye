from kafka import KafkaProducer
import cv2
import numpy as np
import json

# *******************************************************************
# * Author: 2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
# *******************************************************************

#? for recieving frames we just read the HTTP MJPEG stream from the stream server
class KafkaCon:
    def __init__(self, bootstrap_servers, mjpeg_host):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.host = mjpeg_host #localhost for now

    def connect(self):
        # Connect to Kafka brokers
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            acks=1,                     # Only wait for the leader to ack
            compression_type="snappy",  # Compress messages
            linger_ms=30                # Flush batches every 30ms
        )

    def get_stream(self, topic):
        # Return MJPEG stream URL for cv.VideoCapture
        return "http:/"+self.host+"/"+topic+".mjpeg"

    def send_frame(self, topic, frame):
        #TODO: recieve cv2 img and JPEG encode --> test
        # Encode the image to JPEG format
        success, encoded_image = cv2.imencode('.jpg', frame)
        # Check if encoding was successful
        if not success:
            raise RuntimeError("Failed to encode image to JPEG")
        # Convert the numpy array to string
        jpeg_string = encoded_image.tobytes()
        # Send to Kafka topic
        self.producer.send(topic, value=jpeg_string)

    def send_data(self, topic, data):
        #TODO: JSON format check or JSON encode python interface/object --> test
        # JSON encode
        json_string = json.dumps(data, separators=(',', ':'))
        # Send to Kafka topic
        self.producer.send(topic, value=json_string)

    def close(self):
        # Producer connections
        self.producer.close()

## Example usage:
# def main():
#     # start Kafka client
#     kafka_con = KafkaCon(
#         bootstrap_servers='kafka:9092',
#         mjpeg_host='mjpegstreamer:8095'
#     )
#     kafka_con.connect()

#     # define topics
#     in_topic = "camera0"
#     out_topic = "faces-camera0-stream"
#     data_topic = "faces-camera0"

#     # read frames with CV
#     cv2.VideoCapture(kafka_con.get_stream(in_topic))

#     # send frames
#     # -- empty image
#     frame = np.zeros((480, 640, 3), dtype=np.uint8)
#     kafka_con.send_frame(out_topic, frame)

#     # send data
#     faces = ["person1", "person2"]
#     kafka_con.send_data(data_topic, faces)

#     # close Kafka connection when program exits
#     kafka_con.close()