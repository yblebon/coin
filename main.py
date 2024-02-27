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
import click
import importlib
import market
import asyncio_atexit
import monitoring
from decimal import localcontext, Decimal, ROUND_DOWN, Context
from logbook import warn, info, debug, error, StreamHandler
from tasks import task_1, task_dummy


def load_task_module(task_name):
    info("task runner: loading module ...")
    module_name = f'tasks.{task_name}'
    module = importlib.import_module(module_name)
    return importlib.reload(module)

async def task_runner(task_name, pair, fund=0, monitor=False, print_data=False):
    info("task runner: started ...")

    module_task = load_task_module(task_name)
    task = module_task.Task(pair, fund=fund)
    task.init()

    if print_data:
        @market.attach
        async def print_data(msg):
            print(msg)

    if task:
        @market.attach
        async def run_task(msg):
            await task.run(msg)

    if monitor:
        @market.attach
        async def add_tick(msg):
            await monitoring.add_tick(msg)

    # run market
    await market.run(pair)

    asyncio_atexit.register(account.close_session)




@click.command()
@click.option('--pair', default="BTC-USDT", help='Currencies pair')
@click.option('--task', default="task_dummy", help='Task')
@click.option('--prod/--no-prod', default=False)
@click.option('--monitor/--no-monitor', default=False)
@click.option('--fund', default=10, help='Investment fund')
@click.option('--log', default="INFO", help='Log level')
def main(pair, log, task, prod, fund, monitor):
    """Simple program that listen that execute a task on market data level 2 event."""
    account.load_env(prod=prod)
    pair = pair.upper()
    StreamHandler(sys.stdout, level=log).push_application()
    asyncio.get_event_loop().run_until_complete(task_runner(task, pair, fund=fund, monitor=monitor))


if __name__ == "__main__":
    main()
    
