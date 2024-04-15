# ********************************************************************
#   * Author: 2024 Jingdi Lei (@https://github.com/kyrieLei)
# ********************************************************************


import dlib
import numpy as np
import cv2 as cv
import os
import shutil
import time
import logging

detector = dlib.get_frontal_face_detector()


class FaceRegister:
    def __init__(self):
        self.path_photos_from_camera = "Data/data_faces/"
        self.font = cv.FONT_ITALIC
        self.existing_faces_cnt = 0
        self.ss_cnt = 0
        self.current_frame_faces_cnt = 0

        self.save_flag = 1
        self.press_n_flag = 0

        self.frame_time = 0
        self.frame_start_time = 0
        self.fps = 0
        self.fps_show = 0
        self.start_time = time.time()

    def mkdir_store(self):
        if os.path.isdir(self.path_photos_from_camera):
            pass
        else:
            os.mkdir(self.path_photos_from_camera)

    def del_old_face(self):
        folders_rd = os.listdir(self.path_photos_from_camera)
        for i in range(len(folders_rd)):
            shutil.rmtree(self.path_photos_from_camera + folders_rd[i])
        if os.path.isfile("Data/features.csv"):
            os.remove("Data/features.csv")

    def check_existing_faces_cnt(self):
        if os.listdir(self.path_photos_from_camera):
            person_list = os.listdir(self.path_photos_from_camera)
            person_num_list = []
            for person in person_list:
                person_num_list.append(int(person.split('_')[-1]))
            self.existing_faces_cnt = max(person_num_list)

        else:
            self.existing_faces_cnt = 0

    def update_fps(self):
        now = time.time()
        if str(self.start_time).split(".")[0] != str(now).split(".")[0]:
            self.fps_show = self.fps
        self.start_time = now
        self.frame_time = now - self.frame_start_time
        self.fps = 1.0 / self.frame_time
        self.frame_start_time = now

    def draw_note(self, img_rd):
        cv.putText(img_rd, "FPS:   " + str(self.fps_show.__round__(2)), (20, 100), self.font, 0.8, (0, 255, 0), 1,
                   cv.LINE_AA)
        cv.putText(img_rd, "Faces: " + str(self.current_frame_faces_cnt), (20, 140), self.font, 0.8, (0, 255, 0), 1,
                   cv.LINE_AA)
        cv.putText(img_rd, "N: Create face folder", (20, 350), self.font, 0.8, (255, 255, 255), 1, cv.LINE_AA)
        cv.putText(img_rd, "S: Save current face", (20, 400), self.font, 0.8, (255, 255, 255), 1, cv.LINE_AA)
        cv.putText(img_rd, "Q: Quit", (20, 450), self.font, 0.8, (255, 255, 255), 1, cv.LINE_AA)

def process(stream):
    face_recog = FaceRegister()



    face_recog.mkdir_store()

    face_recog.check_existing_faces_cnt()

    while stream.isOpened():
        flag, frame = stream.read()
        k = cv.waitKey(1)
        faces = detector(frame)

        if k == ord('n'):
            face_recog.existing_faces_cnt += 1
            current_face_dir = face_recog.path_photos_from_camera + "person_" + str(face_recog.existing_faces_cnt)
            os.mkdir(current_face_dir)
            logging.info("\n%-40s %s", "Create folders:", current_face_dir)

            face_recog.ss_cnt = 0
            face_recog.press_n_flag = 1

        if len(faces) != 0:
            for i, d in enumerate(faces):
                height = (d.bottom() - d.top())
                width = (d.right() - d.left())
                hh = int(height / 2)
                ww = int(width / 2)

                if (d.right() + ww) > 1400 or (d.bottom() + hh > 1100) or (d.left() - ww < 0) or (d.top() - hh < 0):
                    color = (0, 0, 255)
                    save_flag = 0
                    if k == ord('s'):
                        pass
                        logging.warning("please keep far from your present position")

                else:
                    color = (255, 255, 255)
                    save_flag = 1

                cv.rectangle(frame, tuple([d.left() - ww, d.top() - hh]),
                             tuple([d.right() + ww, d.bottom() + hh]),
                             color, thickness=2)
                img_blank = np.zeros((int(height*2), width*2, 3), np.uint8)

                if save_flag:

                    if k == ord('s'):

                        if face_recog.press_n_flag:
                            face_recog.ss_cnt += 1
                            for ii in range(height*2):
                                for jj in range(width*2):
                                    img_blank[ii][jj] = frame[d.top() - hh + ii][d.left() - ww + jj]
                            cv.imwrite(current_face_dir + "/img_face_" + str(face_recog.ss_cnt) + ".jpg", img_blank)
                            logging.info("%-40s %s/img_face_%s.jpg", "Save into：",
                                          str(current_face_dir), str(face_recog.ss_cnt))
                        else:
                            pass
                            logging.warning("Please press 'N' and then press 'S'")

        face_recog.current_frame_faces_cnt = len(faces)

        face_recog.draw_note(frame)

        if k == ord('q'):
            break

        face_recog.update_fps()
        """#############################################看这里############################################"""
        # cv.imshow("camera", frame)

        ret, buffer = cv.imencode('.jpg', frame)
        img = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
            # logging.debug("Frame ends\n\n")
    stream.release()
    cv.destroyAllWindows()
    """#############################################看这里############################################"""

    # def run(self):
    #     cap = cv.VideoCapture(0)
    #     self.process(cap)
    #     cap.release()
    #     cv.destroyAllWindows()


# def main():
#     logging.basicConfig(level=logging.INFO)
#     face_recog = FaceRegister()
#     face_recog.run()
#
#
# if __name__ == '__main__':
#     main()
