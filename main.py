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
import book
from decimal import localcontext, Decimal, ROUND_DOWN, Context
from logbook import warn, info, debug, error, StreamHandler
from tasks import task_dummy

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())

def get_ws_url():
    r = requests.post('https://api.kucoin.com/api/v1/bullet-public')
    data = r.json()["data"]
    token = data["token"]
    endpoint = data['instanceServers'][0]['endpoint']
    ping_interval = data['instanceServers'][0]['pingInterval']
    ws_url = f"{endpoint}/?token={token}"
    return ws_url

async def task_runner(pair, task=None):
    info("task runner: started ...")
    task.init()
    ws_url = get_ws_url()
    last_pong = 0
    default_ping_interval = 10
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

            await task.run(resp)



@click.command()
@click.option('--pair', default="BTC-USDT", help='Currencies pair')
@click.option('--log', default="INFO", help='Log level')
def main(pair, log):
    """Simple program that listen that execute a task on market data level 2 event."""
    account.load_env()
    pair = pair.upper()
    StreamHandler(sys.stdout, level=log).push_application()
    asyncio.get_event_loop().run_until_complete(task_runner(pair, task=task_dummy.Task(pair)))


if __name__ == "__main__":
    main()
    
