import asyncio
import websockets
import json
import os
import cv2 as cv
import numpy as np
from io import BytesIO
from PIL import Image
import base64
import time
from datetime import datetime
import dlib
from VideoProcess.Face_store import face_store
from VideoProcess.Face_read import FaceRegister

# *******************************************************************
# * Author: 2024 Kael (956136864@qq.com)
# *         2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
# *******************************************************************

# TODO: --> send replies to websocket and parse from client.js

# TODO: monitor kafaka data channel, local cache and send via websocket on request

detector = dlib.get_frontal_face_detector()
# esp_cam = cv.VideoCapture(0 ) 

async def handle_message(websocket):
    face_recog = FaceRegister()
    face_recog.mkdir_store()
    face_recog.check_existing_faces_cnt()
        
    async for message in websocket:
        try:
            # -- receive images from websocket
            frame =  np.frombuffer(message, np.uint8)
            frame = cv.imdecode(frame, cv.IMREAD_COLOR)
            
            faces = detector(frame)
            face_recog.current_frame_faces_cnt = len(faces)

            #! only draw frame and text for debug save
            # face_recog.draw_note(frame)

            #* DEBUG, SAVE ALL CAPTURED IMAGES
            # if len(faces) == 1:
            #     d = faces[0]
            #     height = (d.bottom() - d.top())
            #     width = (d.right() - d.left())
            #     hh = int(height / 2)
            #     ww = int(width / 2)
            #     color = (0, 255, 0)
            #     copied_frame = frame.copy()         #! copy frame here to not write over the original face
            #     face_recog.draw_note(copied_frame)
            #     cv.rectangle(copied_frame, tuple([d.left() - ww, d.top() - hh]),
            #                     tuple([d.right() + ww, d.bottom() + hh]),
            #                     color, thickness=2)
            #     cv.imwrite('./VideoProcess/Data/ws_recieved/'+datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.jpg', copied_frame)


        except Exception as e:
            # -- receive actions from websocket
            # face_recog.update_fps()
            data=json.loads(message)
            key = data.get('action')

            if key == 'r':
                print("New dir")
                # face_recog.existing_faces_cnt += 1
                #? get the person name from the websock message here
                person_name = data.get('name')
                face_recog.path_photos_from_camera = './VideoProcess/Data/data_faces/' + person_name
                if not os.path.isdir(face_recog.path_photos_from_camera):
                    os.makedirs(face_recog.path_photos_from_camera )
                
                current_face_dir = face_recog.path_photos_from_camera 
                # current_face_dir = face_recog.path_photos_from_camera + "/person_" + str(face_recog.existing_faces_cnt)
                # os.mkdir(current_face_dir)

                face_recog.ss_cnt = 0
                face_recog.press_n_flag = 1
                #! send reply
                await websocket.send('{"ok": true, "msg":"Made folder for new face.", "notif": true}')
                print("Made folder for new face.")


            if len(faces) == 1:
                print("One face detected, enable img saving")
                #! send reply
                await websocket.send('{"ok": true, "msg":"One face detected, enable img saving", "notif": false}')
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
                        #! send reply
                        await websocket.send('{"ok": false, "msg":"crop out of range", "notif": true}')
                        pass

                else:
                    color = (255, 255, 255)
                    save_flag = 1
                    #! send reply
                    await websocket.send('{"ok": false, "msg":"No face detected in IMG", "notif": false}')

                
                cv.rectangle(frame, tuple([d.left() - ww, d.top() - hh]),
                            tuple([d.right() + ww, d.bottom() + hh]),
                            color, thickness=2)
                img_blank = np.zeros((int(height*2), width*2, 3), np.uint8)
                # cv.imshow('rec',frame)
                # cv.waitKey(1)
                
            else: 
                save_flag = 0
                
            if save_flag:
                if key == 's':
                    if face_recog.press_n_flag:
                        print("New folder found, successfully saved a img")     
                        #! send reply
                        await websocket.send('{"ok": true, "msg":"New folder found, successfully saved a img", "notif": false}')         
                        face_recog.ss_cnt += 1
                        for ii in range(height*2):
                            for jj in range(width*2):
                                img_blank[ii][jj] = frame[d.top() - hh + ii][d.left() - ww + jj]
                        cv.imwrite(current_face_dir + "/img_face_" + str(face_recog.ss_cnt) + ".jpg", img_blank)
                        await websocket.send('{"ok": true, "msg":"Save img to face storage succeeded.", "notif": true}')
                        ## -- send information
                    else:
                        print("New folder negitive")     
                        #! send reply
                        await websocket.send('{"ok": false, "msg":"New folder not found", "notif": true}')       
                        pass

            if key == 'q':
                print("Updating face storage...")            
                await websocket.send('{"ok": true, "msg":"Updating face storage DB...", "notif": true}')
                # face_store("../AIProcess-Data/data_faces/" )
                face_store("./VideoProcess/Data/data_faces/" )
                print("Updated face storage")            
                await websocket.send('{"ok": true, "msg":"Updated face storage DB complete", "notif": true}')

    


if __name__=="__main__":
    server=websockets.serve(handle_message, "0.0.0.0", 8100)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

