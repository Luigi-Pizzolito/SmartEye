# Import Kafka connection
from kafka import KafkaConsumer
from http.server import BaseHTTPRequestHandler, HTTPServer
import asyncio
import threading
import json
import os

# *******************************************************************
# * Author: 2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
# *******************************************************************

# Dictionary to store messages
message_dict = {}

# Kafka consumer function
def consume():
    consumer = KafkaConsumer(os.environ["DATA_TOPIC"], bootstrap_servers=os.environ["KAFKA_SERVERS"])
    print('Started Kafka consumer.')
    try:
        for msg in consumer:
            # Decode JSON message and update dictionary
            try:
                decoded_msg = json.loads(msg.value.decode('utf-8'))
                camera = decoded_msg.get('camera')[:-7]
                if camera not in message_dict:
                    message_dict[camera] = {}
                
                # Update message_dict based on the received message
                for key, value in decoded_msg.items():
                    if key != 'camera':
                        if key == 'faces':
                            message_dict[camera][key] = value if isinstance(value, list) else [value]
                        else:
                            message_dict[camera][key] = value
                # print("Updated dictionary with message:", decoded_msg)
            except json.JSONDecodeError:
                print("Failed to decode message:", msg.value)

            # print(message_dict)

            # Sleep briefly to allow other coroutines to run
            # await asyncio.sleep(0.2)
    finally:
        consumer.close()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/data':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            data = json.dumps(message_dict)
            self.wfile.write(data.encode('utf-16'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')

def runserver(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=int(os.environ["DATA_PORT"])):
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server listening on port {port}...")
    httpd.serve_forever()
# Main function
async def main():
    loop = asyncio.get_running_loop()
    # Start Kafka consumer in a separate thread
    consume_thread = threading.Thread(target=consume)
    consume_thread.start()
    # Run the HTTP server
    await loop.run_in_executor(None, runserver)

if __name__ == "__main__":
    print("Starting data bridge for", os.environ["DATA_TOPIC"])

    # Run
    asyncio.run(main())
