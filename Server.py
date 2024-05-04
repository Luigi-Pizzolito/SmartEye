import asyncio
import websockets
import json

async def handle_message(websocket):
    async for message in websocket:
        try:
            data=json.loads(message)
            action=data.get('action')
            print(action)
        except Exception as e:
            print("get_error")


if __name__=="__main__":
    server=websockets.serve(handle_message, "localhost", 8094)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

