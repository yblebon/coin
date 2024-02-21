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
import importlib
import book
from decimal import localcontext, Decimal, ROUND_DOWN, Context
from logbook import warn, info, debug, error, StreamHandler
from tasks import task_1, task_dummy

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

def load_task_module(task_name):
    info("task runner: loading module ...")
    module_name = f'tasks.{task_name}'
    module = importlib.import_module(module_name)
    return importlib.reload(module)

async def task_runner(task_name, pair, fund=0):
    info("task runner: started ...")

    module_task = load_task_module(task_name)
    task = module_task.Task(pair, fund=fund)
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
@click.option('--task', default="task_dummy", help='Task')
@click.option('--prod/--no-prod', default=False)
@click.option('--fund', default=10, help='Investment fund')
@click.option('--log', default="INFO", help='Log level')
def main(pair, log, task, prod, fund):
    """Simple program that listen that execute a task on market data level 2 event."""
    account.load_env(prod=prod)
    pair = pair.upper()
    StreamHandler(sys.stdout, level=log).push_application()
    asyncio.get_event_loop().run_until_complete(task_runner(task, pair, fund=fund))


if __name__ == "__main__":
    main()
    
