# SmartEye
 Multi-view web camera IoT system with realtime AI processing.

<!-- TODO: fill in README.md -->

## Running Full System
1. Make sure you have Docker installed.
2. Set the camera configurations in `config.env`.
2. Run `./setup.sh` to generate the configuration from `config.env`.
3. Run `docker compose up --build` to run the system.
4. Press `Ctrl+C` to stop and run `docker compose down` to take the system down.

### Running just Web UI
If you want to test and run just the webui server, you can:
```bash
cd WebInterface
python -m http.server 8094
```
In both cases, you can access the website at [`http://localhost:8094`](http://localhost:8094).

### Interface Endpoints
- Web Interface
    - [`http://localhost:8094`](http://localhost:8094)
- Video Streams
    - [List of streams & FPS](http://localhost:8095/list)
    - Individual streams
        - [`http://localhost:8095/<stream_name>.mjpeg`](http://localhost:8095/.mjpeg)
<!-- TODO: add API Server endpoints -->

<!-- ## Project Directory Structure -->
<!-- TODO: explanation of project directory structure -->

<!-- ## Explanation of Docker System -->
<!-- TODO: explanation of Docker system -->
<!-- TODO: explanation of packaging containers for each programming language -->