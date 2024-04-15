#!/bin/sh

source ../Video_Detection_Part/venv/bin/activate
export KAFKA_SERVERS=192.168.1.103:29092
export MJPEG_SERVER=192.168.1.103:8095
export IN_TOPIC=camera0-stream
export OUT_TOPIC_FACE=camera0-faces-stream
export DATA_TOPIC_FACE=camera0-faces-data
export OUT_TOPIC_POSE=camera0-pose-stream
export DATA_TOPIC_POSE=camera0-pose-data
export OUT_TOPIC_GESTURE=camera0-gesture-stream
export DATA_TOPIC_GESTURE=camera0-gesture-data
python main.py