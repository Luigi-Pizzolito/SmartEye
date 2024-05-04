import asyncio
import websockets
import json
import os
import cv2
import time
import signal
from flask import Flask
from flask.signals import signals_available
from VideoProcess.Face_store import face_store
from kafkacon import KafkaCon

kafka_con = KafkaCon(
        bootstrap_servers=os.environ["KAFKA_SERVERS"],
        mjpeg_host=os.environ["MJPEG_SERVER"]
    )
kafka_con.connect()
in_topic = os.environ["IN_TOPIC"]
esp_cam = cv2.VideoCapture(kafka_con.get_stream(in_topic))  

async def handle_message(websocket):
    async for message in websocket:
        data=json.loads(message)
        action=data.get('action')
        # print(action)
        if action == 's':
            for i in range(5 ):
                ret, img = esp_cam.read()
                cv2.imwrite('./VideoProcess/Data/face_from_kafka/person_new/img' + str(i) + '.jpg', img)
                time.sleep(0.4)
            # -- imgs store
    
            face_store(path='./VideoProcess/Data/face_from_kafka/' )



if __name__=="__main__":
    server=websockets.serve(handle_message, "localhost", 8094)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

