import asyncio
import requests
import ssl
import certifi
import websockets
import json
import uuid
import time
import sys
import account
import tomllib
from logbook import warn, info, StreamHandler

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


def load_env():
    with open(".env.toml", "rb") as f:
        data = tomllib.load(f)
        return data

def get_currency_detail(currency):
    r = requests.get(f'https://api.kucoin.com/api/v3/currencies/{currency}')
    data = r.json()
    return data

def get_ws_url():
    r = requests.post('https://api.kucoin.com/api/v1/bullet-public')
    data = r.json()["data"]
    token = data["token"]
    endpoint = data['instanceServers'][0]['endpoint']
    ping_interval = data['instanceServers'][0]['pingInterval']
    ws_url = f"{endpoint}/?token={token}"
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
            info(resp)

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
    env = load_env()
    credentials = env['credentials']
    account.get_balance(credentials['key'], credentials['secret'], credentials['passphrase'])
    
    pair = "BTC-USDT".upper()
    currency_1, currency_2 = pair.split("-")
    currency_1_detail = get_currency_detail(currency_1)
    currency_2_detail = get_currency_detail(currency_2)
    StreamHandler(sys.stdout).push_application()
    asyncio.get_event_loop().run_until_complete(main(pair))
