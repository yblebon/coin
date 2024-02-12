import asyncio
import requests
import ssl
import certifi
import websockets
import json
import uuid
import time

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())

def get_ws_url():
    r = requests.post('https://api.kucoin.com/api/v1/bullet-public')
    data = r.json()["data"]
    token = data["token"]
    endpoint = data['instanceServers'][0]['endpoint']
    ping_interval = data['instanceServers'][0]['pingInterval']
    ws_url = f"{endpoint}/?token={token}"
    print(data)

    return ws_url

async def main(pair):
    ws_url = get_ws_url()
    last_pong = 0
    default_ping_interval = 10
    async with websockets.connect(ws_url, ssl=ssl_context) as ws:
        # ping
        await ws.send(json.dumps({
          "id": str(uuid.uuid4()),
          "type": "ping"
        }))

        # subscribe
        await ws.send(json.dumps({
          "id": str(uuid.uuid4()),
          "type": "subscribe",
          "topic": f"/market/level2:{pair}",
        }))

        while True:
            resp = await ws.recv()
            resp = json.loads(resp)
            print(resp)

            # update last pong
            if (resp["type"] == "pong"):
                last_pong = time.time()

            should_ping = (time.time() - last_pong) > default_ping_interval

            # send ping
            if should_ping:
                await ws.send(json.dumps({
                    "id": str(uuid.uuid4()),
                    "type": "ping"
                }))


if __name__ == "__main__":
    pair = "BTC-USDT"
    asyncio.get_event_loop().run_until_complete(main(pair))
