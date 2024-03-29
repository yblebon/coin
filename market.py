
import websockets
import ssl
import certifi
import sys
import asyncio
import requests
import json
import uuid
import time
from logbook import warn, info, debug, error, StreamHandler

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())

subscribers = []

def get_ws_url():
    r = requests.post('https://api.kucoin.com/api/v1/bullet-public')
    data = r.json()["data"]
    token = data["token"]
    endpoint = data['instanceServers'][0]['endpoint']
    ping_interval = data['instanceServers'][0]['pingInterval']
    ws_url = f"{endpoint}/?token={token}"
    return ws_url



def attach(subscriber):
    if subscriber not in subscribers:
        subscribers.append(subscriber)

async def publish(msg):
    results = await asyncio.gather(*[subscriber(msg) for subscriber in subscribers])

async def run(pair):

    ws_url = get_ws_url()
    last_pong = 0
    default_ping_interval = 10

    info(f"market price: connection to {ws_url} ...")
    async with websockets.connect(ws_url, ssl=ssl_context) as ws:
            info("market price: connected ...")
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

                # tick 
                if resp['type'] == "message" and resp['topic']  == f"/market/level2:{pair}":
                    for tick in resp['data']['changes']['asks']:
                        date, price, qty = float(resp['data']['time']), float(tick[0]), float(tick[1])
                        await publish(('A', date, price, qty ))
                    for tick in resp['data']['changes']['bids']:
                        date, price, qty = float(resp['data']['time']), float(tick[0]), float(tick[1])
                        await publish(('B', date, price, qty ))

if __name__ == "__main__":
    StreamHandler(sys.stdout, level="DEBUG").push_application()
    asyncio.get_event_loop().run_until_complete(run("BTC-USDT"))
