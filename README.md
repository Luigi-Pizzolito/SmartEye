# SmartEye
 Multi-view web camera IoT system with realtime AI processing.

<!-- TODO: fill in README.md -->

## Running Full System
1. Make sure you have Docker installed.
2. Set the camera configurations in `config.env`.
2. If you're using Linux, run `./setup.sh` to generate the configuration from `config.env`.<br>
   If you're using Windows, run `./setup_windows.sh` to generate the configuration from `config.env`.
3. Run `docker compose up --build` to run the system.
4. Press `Ctrl+C` to stop and run `docker compose down` to take the system down.

### Interface Endpoints
- Web Interface
    - [`http://localhost:8094`](http://localhost:8094)
    - Running just Web UI also possible:
        - `cd WebInterface`
        - `python -m http.server 8094`
- Internal Endpoints
    - Video Streams
        - Internal video stream redistributor / multi-client broadcast with XHR HTTP JSON endpoint for listing current streams.
        - [List of streams & FPS](http://localhost:8095/list)
        - Individual streams:
            - [`http://localhost:8095/<stream_name>.mjpeg`](http://localhost:8095/.mjpeg)
    - Data API Server
        - [Live AI Detection Data](http://localhost:8200/data)
        - In JSON format as HTTP XHR endpoint.
    - Face Register WebSocket API Server
        - One instance for each camera, availble per camera ID.
        - At `ws://localhost:8100-81XX` with JSON format.
        - Requires AI Processing restart for update.
    - Kafka WebUI
        - For debugging purposes, a Web UI for Kafka is included.
        - [Kafka WebUI](http://localhost:8092)
        - Kafka is exposed to the host at `localhost:29092`.
    - Stream local webcam instead of ESP-CAM for testing purposes.
        - Activate local `venv`
        - Run `python stream_usbcam.py`

<!-- ## Explanation of Docker System -->
<!-- TODO: explanation of Docker system -->
<!-- TODO: explanation of packaging containers for each programming language -->

## Project Directory Structure
Below is a tree of the project directory structure with an explanation of the purpose of each file/directory:
```
SmartEye
├── ESP32CAM-Firmware                   (Arduino code for ESP-CAM Firmware)
│
│
├── dockerfiles                         (Docker image build files)
│   ├── AIProcess-API.Dockerfile        (Environment for WS Face API)
│   ├── AIProcess-Data.Dockerfile       (Environment for AI Data API)
│   ├── AIProcess.Dockerfile            (Environment for AI Process)
│   ├── MJPEGStreamer.Dockerfile        (Environment for stream distributor)
│   └── VideoBuffer.Dockerfile          (Environment for ESP-CAM video buffer)
│
├── docker-template                     (Docker template generation from config.env)
│   ├── docker-compose.yml.jinja        (Base Template)
│   └── generate_template.py            (Generator script)
│
│
├── AIProcess-Data                      (AI Processing Data Store)
│   ├── data_dlib                       (Model Weights for face recognition)
│   ├── data_faces                      (Individual faces registration images)
│   └── features.csv                    (Extracted registration facial features)
│
├── AIProcess-Kafka                     (Code for AI processing of camera feeds)
│   ├── VideoProcess                    (Sub-classes for each algorithm)
│   │   ├── Face_read.py
│   │   ├── Face_store.py
│   │   ├── KafkaFace.py
│   │   ├── KafkaHand.py
│   │   └── KafkaPose.py
│   ├── kafkacon.py                     (Class for Kafka connections)
│   ├── main.py                         (main.py for AI processing)
│   ├── Servedata.py                    (main.py for Kafka AI Data API)
│   └── Server.py                       (main.py for AI Face Register WS API)
│
├── MJPEGStreamer                       (Code for stream redistributor)
│   ├── bcast.go                        (Class for one-to-many broadcast)
│   ├── fps.go                          (Class for FPS counting)
│   ├── kafka.go                        (Class for Kafka connection)
│   ├── main.go                         (Main program)
│   └── mjpeg.go                        (Class for MJPEG encoding)
│
├── VideoBuffer                         (Code for ESP-CAM video buffer)
│   ├── env.go                          (Class for getting configuration)
│   ├── kafka.go                        (Class for Kafka connection)
│   └── main.go                         (Main program)
│
├── WebInterface                        (Client code for web interface)
│   ├── assets                          (CSS/JS/IMG assets)
│   │   ├── css
│   │   ├── img
│   │   └── js
│   ├── docs.html                       (Documentation page)
│   ├── Face_register.html              (Face Register Page)
│   ├── index.html                      (Index page)
│   ├── Login.html                      (User login page)
│   └── Register.html                   (User register page)
│
│
├── config.env                          (Whole-system configuration)
├── README.md                           (This file)
├── setup.sh                            (Docker template generation for Linux)
├── setup_windows.sh                    (Docker template generation for Windows)
└── stream_usbcam.py                    (Testing local webcam streamer)

26 directories, 137 files
```