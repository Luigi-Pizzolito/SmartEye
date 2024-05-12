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
        self.host = mjpeg_host

    def connect(self):
        # Connect to Kafka brokers
        self.producer = KafkaProducer(
            security_protocol="PLAINTEXT",
            api_version="3.7",
            bootstrap_servers=self.bootstrap_servers,
            acks=0,                     # Only wait for the leader to ack
            compression_type="snappy",  # Compress messages
            linger_ms=30                # Flush batches every 30ms
        )

    def get_stream(self, topic):
        # Return MJPEG stream URL for cv.VideoCapture
        return "http:/"+self.host+"/"+topic+".mjpeg"

    def send_frame(self, topic, frame):
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
        # JSON encode
        json_string = json.dumps(data, separators=(',', ':'))
        # Send to Kafka topic
        self.producer.send(topic, value=json_string.encode('utf-8'))

    def close(self):
        # Producer connections
        self.producer.close()