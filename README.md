# SmartEye
 Multi-view web camera IoT system with realtime AI processing.

<!-- TODO: fill in README.md -->

## Running Full System
1. Make sure you have Docker installed.
2. Run `docker compose up --build` to run the system.
3. Press `Ctrl+C` to stop and run `docker compose down` to take the system down.

### Running just Web UI
If you want to test and run just the webui server, you can:
```bash
cd WebInterface
python -m http.server 8094
```
In both cases, you can access the website at `http://localhost:8094`.