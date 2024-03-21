import logging

from Face_store import detector,predictor,face_reco_model
import cv2 as cv
import time
import numpy as np
import pandas as pd
import os

class FaceRecognizer:
    def __init__(self):
        self.font = cv.FONT_ITALIC

        # FPS
        self.frame_time = 0
        self.frame_start_time = 0
        self.fps = 0
        self.fps_show = 0
        self.start_time = time.time()

        self.frame_cnt = 0

        # 用来存放所有录入人脸特征的数组
        self.face_features_known_list = []
        # 存储录入人脸名字
        self.face_name_known_list = []

        # 用来存储上一帧和当前帧 ROI 的质心坐标
        self.last_frame_face_centroid_list = []
        self.current_frame_face_centroid_list = []

        # 用来存储上一帧和当前帧检测出目标的名字
        self.last_frame_face_name_list = []
        self.current_frame_face_name_list = []

        # 上一帧和当前帧中人脸数的计数器
        self.last_frame_face_cnt = 0
        self.current_frame_face_cnt = 0

        # 用来存放进行识别时候对比的欧氏距离
        self.current_frame_face_X_e_distance_list = []

        # 存储当前摄像头中捕获到的所有人脸的坐标名字
        self.current_frame_face_position_list = []
        # 存储当前摄像头中捕获到的人脸特征
        self.current_frame_face_feature_list = []

        #欧式距离
        self.last_current_frame_centroid_e_distance = 0

        # 控制再识别的后续帧数
        # 如果识别出 "unknown" 的脸, 将在 reclassify_interval_cnt 计数到 reclassify_interval 后, 对于人脸进行重新识别
        self.reclassify_interval_cnt = 0
        self.reclassify_interval = 10

    def get_faces_database(self):
        path_features_known_csv = "Data/features.csv"
        if os.path.exists(path_features_known_csv):

            csv_rd = pd.read_csv(path_features_known_csv, header=None)
            for i in range(csv_rd.shape[0]):
                features_someone_arr = []
                self.face_name_known_list.append(csv_rd.iloc[i][0])
                for j in range(1, 129):
                    if csv_rd.iloc[i][j] == '':
                        features_someone_arr.append('0')
                    else:
                        features_someone_arr.append(csv_rd.iloc[i][j])
                self.face_features_known_list.append(features_someone_arr)
            
            return True
        else:
            print("'features_all.csv' not found!")
            print("Please run 'get_faces_from_camera.py' "
                            "and 'features_extraction_to_csv.py' before 'face_reco_from_camera.py'")
            return False

    #利用质心进行人脸跟踪，这个方法就是计算一帧中每一张人脸的质心位置和下一帧中人脸的质心位置，找最小距离的质心，找到后进行特征匹配,可以快速识别而非重新做模版匹配
    def centroid_tracker(self):
        for i in range(len(self.current_frame_face_centroid_list)):
            e_distance_current_frame_person_x_list=[]
            for j in range(len(self.last_frame_face_centroid_list)):
                #计算相邻两张帧
                self.last_current_frame_centroid_e_distance=self.distance(
                    self.current_frame_face_centroid_list[i]-self.last_frame_face_centroid_list[j]
                )
                e_distance_current_frame_person_x_list.append(
                    self.last_current_frame_centroid_e_distance
                )
            last_frame_num=e_distance_current_frame_person_x_list.index(
                min(e_distance_current_frame_person_x_list)
            )

            self.current_frame_face_name_list[i]=self.last_frame_face_name_list[last_frame_num]



    def update_fps(self):
        now = time.time()
        # 每秒刷新 fps / Refresh fps per second
        if str(self.start_time).split(".")[0] != str(now).split(".")[0]:
            self.fps_show = self.fps
        self.start_time = now
        self.frame_time = now - self.frame_start_time
        self.fps = 1.0 / self.frame_time
        self.frame_start_time = now

    @staticmethod
    def distance(feature_1,feature_2):
        fea_1=np.array(feature_1)
        fea_2 = np.array(feature_2)
        return np.linalg.norm(fea_1-fea_2)

    def draw_note(self, img_rd):
        # 添加说明
        cv.putText(img_rd, "Face Recognizer with OT", (20, 40), self.font, 1, (255, 255, 255), 1, cv.LINE_AA)
        cv.putText(img_rd, "Frame:  " + str(self.frame_cnt), (20, 100), self.font, 0.8, (0, 255, 0), 1,
                    cv.LINE_AA)
        cv.putText(img_rd, "FPS:    " + str(self.fps.__round__(2)), (20, 130), self.font, 0.8, (0, 255, 0), 1,
                    cv.LINE_AA)
        cv.putText(img_rd, "Faces:  " + str(self.current_frame_face_cnt), (20, 160), self.font, 0.8, (0, 255, 0), 1,
                    cv.LINE_AA)
        cv.putText(img_rd, "Q: Quit", (20, 450), self.font, 0.8, (255, 255, 255), 1, cv.LINE_AA)

        for i in range(len(self.current_frame_face_name_list)):
            img_rd = cv.putText(img_rd, "Face_" + str(i + 1), tuple(
                [int(self.current_frame_face_centroid_list[i][0]), int(self.current_frame_face_centroid_list[i][1])]),
                                 self.font,
                                 0.8, (255, 190, 0),
                                 1,
                                 cv.LINE_AA)

    def process(self,stream):
        if self.get_faces_database():
            while stream.isOpened():
                self.frame_cnt +=1
                logging.debug("Frame"+str(self.frame_cnt)+"starts")
                flag, img=stream.read()
                k=cv.waitKey(1)

                #检测人脸
                faces = detector(img)

                #更新当前帧的人脸
                self.last_frame_face_cnt=self.current_frame_face_cnt
                self.current_frame_face_cnt=len(faces)

                #更新人脸名字列表
                self.last_frame_face_name_list = self.current_frame_face_name_list[:]

                # 更新上一帧和当前帧的质心列表 / update frame centroid list
                self.last_frame_face_centroid_list = self.current_frame_face_centroid_list
                self.current_frame_face_centroid_list = []

                if (
                        self.current_frame_face_cnt == self.last_frame_face_cnt
                        and self.reclassify_interval_cnt!= self.reclassify_interval
                ):
                    logging.debug("Scene 1: No face changed")
                    self.current_frame_face_position_list=[]
                    if "unknown" in self.current_frame_face_name_list:
                        logging.debug("检测到未知人脸")
                        self.reclassify_interval_cnt+=1


                    if self.current_frame_face_cnt !=1:
                        self.centroid_tracker()

                    if self.current_frame_face_cnt !=0:

                        #先画一个框
                        for i ,d in enumerate(faces):
                            self.current_frame_face_position_list.append(tuple(
                                [faces[i].left(), int(faces[i].bottom() + (faces[i].bottom() - faces[i].top()) / 4)]))
                            self.current_frame_face_centroid_list.append(
                                [int(faces[i].left() + faces[i].right()) / 2,
                                 int(faces[i].top() + faces[i].bottom()) / 2]
                            )
                            img=cv.rectangle(img,tuple([d.left(),d.top()]),tuple([d.right(),d.bottom()]),(255,255,255),thickness=4)
                    #再写上名字
                    for i in range(self.current_frame_face_cnt):

                        img_rd = cv.putText(img, self.current_frame_face_name_list[i],
                                             self.current_frame_face_position_list[i], self.font, 0.8, (0, 255, 255), 1,
                                             cv.LINE_AA)
                    self.draw_note(img)

                else:
                    logging.debug("Scene 2: Faces cnt changes in this frame")
                    self.current_frame_face_position_list = []
                    self.current_frame_face_X_e_distance_list = []
                    self.current_frame_face_feature_list = []
                    self.reclassify_interval_cnt = 0

                    #若当前没有人脸
                    if self.current_frame_face_cnt ==0:
                        logging.debug("No faces in this frame")
                        self.current_frame_face_name_list=[]
                    else:
                        logging.debug("Get faces in this frame")
                        self.current_frame_face_name_list=[]
                        for i in range(len(faces)):
                            shape=predictor(img,faces[i])
                            self.current_frame_face_feature_list.append(
                                face_reco_model.compute_face_descriptor(img,shape)
                            )
                            self.current_frame_face_name_list.append("unknown")

                        for j in range(len(faces)):
                            logging.debug("  For face %d in current frame:", j + 1)
                            self.current_frame_face_centroid_list.append(
                                [int(faces[j].left() + faces[j].right()) / 2,
                                 int(faces[j].top() + faces[j].bottom()) / 2])

                            self.current_frame_face_X_e_distance_list = []

                            self.current_frame_face_position_list.append(tuple(
                                [faces[j].left(), int(faces[j].bottom() + (faces[j].bottom() - faces[j].top()) / 4)]))

                            # For every faces detected, compare the faces in the database
                            for i in range(len(self.face_features_known_list)):
                                # 如果 q 数据不为空
                                if str(self.face_features_known_list[i][0]) != '0.0':
                                    e_distance_tmp = self.distance(
                                        self.current_frame_face_feature_list[k],
                                        self.face_features_known_list[i])
                                    logging.debug("      with person %d, the e-distance: %f", i + 1, e_distance_tmp)
                                    self.current_frame_face_X_e_distance_list.append(e_distance_tmp)
                                else:
                                    self.current_frame_face_X_e_distance_list.append(999999999)


                            similar_person_num=self.current_frame_face_X_e_distance_list.index(
                                min(self.current_frame_face_X_e_distance_list)
                            )


                            if min(self.current_frame_face_X_e_distance_list) < 0.4:
                                self.current_frame_face_name_list[j] = self.face_name_known_list[similar_person_num]
                                logging.debug("  Face recognition result: %s",
                                              self.face_name_known_list[similar_person_num])
                            else:
                                logging.debug("  Face recognition result: Unknown person")

                        self.draw_note(img)

                if k == ord('q'):
                    break
                self.update_fps()
                cv.imshow("Camera",img)
                logging.debug("Frame ends\n\n")


    def run(self):
        cap=cv.VideoCapture(0)
        self.process(cap)

        cap.release()
        cv.destroyAllWindows()














def main():
    logging.basicConfig(level=logging.INFO)
    Face_Recognizer = FaceRecognizer()
    Face_Recognizer.run()


if __name__=='__main__':
    main()