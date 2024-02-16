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
from collections import deque
from operator import itemgetter

from logbook import warn, info, debug, error, StreamHandler

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())

class Book():
    def __init__(self, pair):
        self.pair = pair
        self.asks  = deque(maxlen=10)
        self.bids = deque(maxlen=10)

    def update_asks(self, tick):
        self.asks.append(tick) 

    def update_bids(self, tick):
        self.bids.append(tick)

    @property
    def last_ask_price(self):
        return self.asks[0][0]

    @property
    def last_bid_price(self):
        return self.bids[0][0]

    @property
    def last_bid_qty(self):
        pass

    @property
    def last_ask_qty(self):
        pass

    @property
    def best_ask_price(self):
        l = sorted(self.asks, key=itemgetter(0))
        return l[0][0]

    @property
    def best_bid_price(self):
        l = sorted(self.bids, key=itemgetter(0))
        return l[-1][0]


class Task_1():
    def __init__(self, pair):
        self.pair = pair
        self.currencies = {}
        self.initialized = False
        self.buy = True
        self.book = Book(self.pair)

    def init(self):
        info("initialization ...")
        currency_1, currency_2 = self.pair.split("-")
        self.currencies[currency_1] = {}
        self.currencies[currency_2] = {}

        self.currencies[currency_1]["detail"] = get_currency_detail(currency_1)
        self.currencies[currency_2]["detail"] = get_currency_detail(currency_2)

        balance = account.get_balance()
        self.currencies[currency_1]["balance"] = account.find_balance(balance, currency_1)
        self.currencies[currency_2]["balance"] = account.find_balance(balance, currency_2)

        debug(balance)


    def sanitize_qty(self, qty):
        return qty

    def sanitize_price(self, price):
        return price


    def exec_buy(self, pair, price, qty):
        price = self.sanitize_price(price)
        qty = self.sanitize_qty(qty)
        r = account.place_buy_order(self.pair, price, qty)
        if r['code'] != '200000':
            error(r)

    async def run(self, event):
        debug(f"event received: {event}")
        if event['type'] == "message" and event['topic']  == f"/market/level2:{self.pair}":
            for tick in event['data']['changes']['asks']:
                self.book.update_asks(tick)
            for tick in event['data']['changes']['bids']:
                self.book.update_bids(tick)

        if self.buy:
            self.exec_buy(self.pair, 344444, 0.4)
            self.buy = False



def get_currency_detail(currency):
    r = requests.get(f'https://api.kucoin.com/api/v3/currencies/{currency}')
    data = r.json()
    debug(data)
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
@click.option('--log', default="INFO", help='Log level')
def main(pair, log):
    """Simple program that listen that execute a task on market data level 2 event."""
    account.load_env()
    pair = pair.upper()
    StreamHandler(sys.stdout, level=log).push_application()
    asyncio.get_event_loop().run_until_complete(task_runner(pair, task=Task_1(pair)))


if __name__ == "__main__":
    main()
    
