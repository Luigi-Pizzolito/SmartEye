import asyncio
import websockets
import json
import os
import cv2 as cv
import numpy as np
import time
import dlib
from VideoProcess.Face_store import face_store
from VideoProcess.Face_read import FaceRegister
# from kafkacon import KafkaCon

# *******************************************************************
# * Author: 2024 Kael (956136864@qq.com)
# *         2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
# *******************************************************************

# TODO: remove kafka input image
# TODO: --> recieve image from websocket
# TODO: --> send replies to websocket and parse from client.js
# TODO: --> add "q" button on the website

detector = dlib.get_frontal_face_detector()
# esp_cam = cv.VideoCapture(0 ) 
# kafka_con = KafkaCon(
#         bootstrap_servers=os.environ["KAFKA_SERVERS"],
#         mjpeg_host=os.environ["MJPEG_SERVER"]
#     )
# kafka_con.connect()
# in_topic = os.environ["IN_TOPIC"]
# esp_cam = cv.VideoCapture(kafka_con.get_stream(in_topic)) 
# --
esp_cam = cv.VideoCapture(0 ) 
# test --

async def handle_message(websocket):
    face_recog = FaceRegister()
    face_recog.mkdir_store()
    face_recog.check_existing_faces_cnt()
    
    while esp_cam.isOpened():
        async for message in websocket:
            flag, frame = esp_cam.read()
            faces = detector(frame)
            face_recog.current_frame_faces_cnt = len(faces)
            face_recog.draw_note(frame)
            # face_recog.update_fps()
            data=json.loads(message)
            key = data.get('action')

            if key == 'r':
                print("New dir")
                face_recog.existing_faces_cnt += 1
                current_timestamp = time.time()
                local_time = str(time.localtime(current_timestamp) )
                time_now = local_time.replace(" ", "")
                face_recog.path_photos_from_camera = '../AIProcess-Data/data_faces/' + time_now
                if not os.path.isdir(face_recog.path_photos_from_camera):
                    os.makedirs(face_recog.path_photos_from_camera )
                
                current_face_dir = face_recog.path_photos_from_camera + "/person_" + str(face_recog.existing_faces_cnt)
                os.mkdir(current_face_dir)

                face_recog.ss_cnt = 0
                face_recog.press_n_flag = 1
                #! send reply
                await websocket.send('{"ok": true, "msg":"Made folder for new face."}')


            if len(faces) == 1:
                print("One face detected, enable img saving")
                d = faces[0]
                height = (d.bottom() - d.top())
                width = (d.right() - d.left())
                hh = int(height / 2)
                ww = int(width / 2)
                if (d.right() + ww) >= frame.shape[1] or (d.bottom() + hh >= frame.shape[0]) or (d.left() - ww < 0) or (d.top() - hh < 0):
                    color = (0, 0, 255)
                    save_flag = 0
                    if key == 's':
                        print("crop out of range")   
                        pass

                else:
                    color = (255, 255, 255)
                    save_flag = 1
                
                cv.rectangle(frame, tuple([d.left() - ww, d.top() - hh]),
                            tuple([d.right() + ww, d.bottom() + hh]),
                            color, thickness=2)
                img_blank = np.zeros((int(height*2), width*2, 3), np.uint8)
                cv.imshow('rec',frame)
                cv.waitKey(1)
                
            else: 
                save_flag = 0
                
            if save_flag:
                if key == 's':
                    if face_recog.press_n_flag:
                        print("New folder found, successfully saved a img")              
                        face_recog.ss_cnt += 1
                        for ii in range(height*2):
                            for jj in range(width*2):
                                img_blank[ii][jj] = frame[d.top() - hh + ii][d.left() - ww + jj]
                        cv.imwrite(current_face_dir + "/img_face_" + str(face_recog.ss_cnt) + ".jpg", img_blank)
                        await websocket.send('{"ok": true, "msg":"Save img to face storage succeeded."}')
                        ## -- send information
                    else:
                        print("New folder negitive")            
                        pass

            if key == 'q':
                print("Updated face storage")            
                await websocket.send('{"ok": true, "msg":"Updated face storage DB"}')
                face_store(face_recog.path_photos_from_camera )

    # --
    esp_cam.release()
    # test --
    # kafka_con.close()
    


if __name__=="__main__":
    server=websockets.serve(handle_message, "0.0.0.0", 8100)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

