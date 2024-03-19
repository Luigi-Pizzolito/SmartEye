import os
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from kafka import KafkaConsumer

# *******************************************************************
# * Author: 2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
# *******************************************************************

# Kafka configuration
bootstrap_servers = 'kafkad:9092'
topic = 'camera0'

# Create Kafka consumer
consumer = KafkaConsumer(topic,
                         bootstrap_servers=bootstrap_servers,
                         auto_offset_reset='earliest',
                         value_deserializer=lambda x: x)

print("Consumer ready")

# Create directory to save images if it doesn't exist
os.makedirs("img", exist_ok=True)

# Counter to generate unique filenames
frame_counter = 0

for msg in consumer:
    print("Got msg")
    # Decode JPG image from Kafka message value
    img_bytes = BytesIO(msg.value)
    img_pil = Image.open(img_bytes)

    # Convert PIL image to OpenCV format
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    # Save image to disk
    filename = f"img/frame_{frame_counter}.jpg"
    cv2.imwrite(filename, img_cv)
    print(f"Saved frame to {filename}")

    # Increment frame counter
    frame_counter += 1

# Close Kafka consumer
consumer.close()
