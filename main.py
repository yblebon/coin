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
import click

from logbook import warn, info, StreamHandler

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


class Task_1():
    def __init__(self, pair):
        self.pair = pair
        self.balance = {}

    def init(self):
        info("initialization ...")
        currency_1, currency_2 = self.pair.split("-")

        currency_1_detail = get_currency_detail(currency_1)
        currency_2_detail = get_currency_detail(currency_2)

        balance = account.get_balance()
        currency_1_balance = account.find_balance(balance, currency_1)
        currency_2_balance = account.find_balance(balance, currency_2)

        info(balance)

        self.balance[currency_1] = currency_1_balance
        self.balance[currency_2] = currency_2_balance

    async def run(self, event):
        info(f"event received: {event}")

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

async def task_runner(pair, task=None):
    task.init()
    ws_url = get_ws_url()
    last_pong = 0
    default_ping_interval = 10
    account.place_buy_order(pair, 344444, 0.4)
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

            await task.run(resp)



@click.command()
@click.option('--pair', default="BTC-USDT", help='Currencies pair')
def main(pair):
    """Simple program that listen that execute a task on market data level 2 event."""
    account.load_env()
    pair = pair.upper()
    StreamHandler(sys.stdout).push_application()
    asyncio.get_event_loop().run_until_complete(task_runner(pair, task=Task_1(pair)))


if __name__ == "__main__":
    main()
    
