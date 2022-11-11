import asyncio
import websockets


async def hello(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            recv_text = await websocket.recv()
            print("> {}".format(recv_text))


asyncio.get_event_loop().run_until_complete(
    hello('ws://127.0.0.1:8099'))