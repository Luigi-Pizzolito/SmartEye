import asyncio
import websockets
import json
import os
import cv2
import time
from VideoProcess.Face_store import face_store
from kafkacon import KafkaCon



async def handle_message(websocket):
    kafka_con = KafkaCon(
        bootstrap_servers=os.environ["KAFKA_SERVERS"],
        mjpeg_host=os.environ["MJPEG_SERVER"]
    )
    kafka_con.connect()
    in_topic = os.environ["IN_TOPIC"]
    esp_cam = cv2.VideoCapture(kafka_con.get_stream(in_topic)) 
     
    async for message in websocket:
        data=json.loads(message)
        action=data.get('action')
        # print(action)
        if action == 's':
            current_timestamp = time.time()
            local_time = str(time.localtime(current_timestamp) )
            time = local_time.replace(" ", "")
            os.makedirs('./VideoProcess/Data/faces_from_kafka/' + time )
            os.makedirs('./VideoProcess/Data/faces_from_kafka/' + time + '/person_new')
            
            path = './VideoProcess/Data/faces_from_kafka/' + time + '/person_new/img'
            for i in range(5 ):
                ret, img = esp_cam.read()
                cv2.imwrite(path + str(i) + '.jpg', img)
                time.sleep(0.4)
            # -- imgs store
    
            face_store(path='./VideoProcess/Data/face_from_kafka/' + time + '/person_new' )
        
    kafka_con.close()
    


if __name__=="__main__":
    server=websockets.serve(handle_message, "localhost", 8094)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

