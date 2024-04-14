# syntax = docker/dockerfile:experimental
# *******************************************************************
# * Author: 2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
# *******************************************************************

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# China Mirror
COPY tunaDebian.list /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y build-essential make
RUN apt-get install -y ffmpeg libsm6 libxext6

# Install any needed dependencies specified in requirements.txt
COPY requirements.txt /app/requirements.txt
# China Mirror
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
# Use experimental external pip cache on host machine to speed up pip
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip pip install --no-cache-dir -r requirements.txt

# Add wait-for-it script
COPY wait-for-it.sh /usr/local/bin/wait-for-it
RUN chmod +x /usr/local/bin/wait-for-it

# Copy the current directory contents into the container at /app
COPY . /app

# Run app.py when the container launches
# CMD ["wait-for-it", "-s", "kafka:9092", "--", "python", "main.py"]
CMD ["python", "main.py"]
