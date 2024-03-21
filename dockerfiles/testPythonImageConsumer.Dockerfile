# *******************************************************************
# * Author: 2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
# *******************************************************************

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run app.py when the container launches
# TODO: add wait-for-it script here
CMD ["python", "main.py"]
