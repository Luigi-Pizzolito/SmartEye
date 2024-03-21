import csv
import os
import dlib
import csv
import numpy as np
import logging
import cv2 as cv

path_images_from_camera="Data/data_faces/"
detector=dlib.get_frontal_face_detector()

#特征检测
predictor=dlib.shape_predictor("Data/data_dlib/shape_predictor_68_face_landmarks.dat")


#人脸识别
face_reco_model=dlib.face_recognition_model_v1("Data/data_dlib/dlib_face_recognition_resnet_model_v1.dat")

def return_128d_features(path_img):
    img=cv.imread(path_img)
    faces=detector(img,1) #数字表示不同的检测模型

    if len(faces) !=0:
        shape=predictor(img,faces[0])
        face_descriptor=face_reco_model.compute_face_descriptor(img,shape)
    else:
        face_descriptor=0
        logging.warning("no face")
    return face_descriptor



def features_mean_PersonX(path_face):
    feature_list_personX=[]
    photos_list=os.listdir(path_face)
    if photos_list:
        for i in range(len(photos_list)):
            logging.info("%-40s %-20s", "Reading image:", path_face + "/" + photos_list[i])
            features_128d = return_128d_features(path_face + "/" + photos_list[i])
            # 遇到没有检测出人脸的图片跳过 / Jump if no face detected from image
            if features_128d == 0:
                i += 1
            else:
                feature_list_personX.append(features_128d)
    if feature_list_personX:
        features_mean_personX = np.array(feature_list_personX, dtype=object).mean(axis=0)
    else:
        features_mean_personX = np.zeros(128, dtype=object, order='C')
    return features_mean_personX


def main():
    logging.basicConfig(level=logging.INFO)
    person_list = os.listdir("Data/data_faces")
    person_list.sort()

    with open("Data/features.csv","w",newline="") as f:
        writer=csv.writer(f)
        for person in person_list:
            logging.info("%sperson_%s", path_images_from_camera, person)
            features_mean = features_mean_PersonX(path_images_from_camera + person)

            if len(person.split('_', 2)) == 2:
                # "person_x"
                person_name = person
            else:
                # "person_x_tom这种类型，之后可以编辑名字"
                person_name = person.split('_', 2)[-1]

            features_mean = np.insert(features_mean, 0, person_name, axis=0)
            writer.writerow(features_mean)
            logging.info('\n')
        logging.info("所有录入人脸数据存入 / Save all the features of faces registered into: data/features_all.csv")


if __name__ == '__main__':
    main()