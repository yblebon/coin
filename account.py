import time
import base64
import hmac
import hashlib
import requests
import uuid
import json
import toml
import sys
from logbook import warn, info, debug, error

api_secret = None
api_key = None
api_passphrase = None
api_orders_endpoint = "api/v1/orders/test"


def load_env(prod=False):
    global api_key
    global api_secret
    global api_passphrase

    try:
        with open(".env.toml", "rb") as f:
            data = toml.loads(f)
            credentials = data['credentials']
            api_key = credentials['key']
            api_secret = credentials['secret']
            api_passphrase = credentials['passphrase']
    except FileNotFoundError:
        error(f"Missing environment file '.env.toml'")
        sys.exit(-1)

    if prod:
        api_orders_endpoint = "api/v1/orders"

def create_headers(endpoint, method, data_json=None):
    now = int(time.time() * 1000)
    str_to_sign = str(now) + method + endpoint

    if data_json:
        str_to_sign = str_to_sign + data_json

    signature = base64.b64encode(hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
    passphrase = base64.b64encode(hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())

    headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": api_key,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2"
    }

    if data_json:
        headers["Content-Type"] = "application/json"

    return headers

def get_balance():
    headers = create_headers('/api/v1/accounts', 'GET')
    r = requests.request('get', 'https://api.kucoin.com/api/v1/accounts', headers=headers)
    data = r.json()
    debug(data)
    return data


def place_buy_order(pair, price, quantity, order_type='market', time_in_force="fok"):
    st_time = time.time()
    payload = {
        'clientOid': str(uuid.uuid4()),
        'side': 'buy',
        'type': order_type,
        'symbol': pair,
        'price': str(price),
        'size': str(quantity),
        'timeInForce': time_in_force
    }
    headers = create_headers(f'/{api_orders_endpoint}', 'POST', data_json=json.dumps(payload))
    r = requests.post(f'https://api.kucoin.com/{api_orders_endpoint}', data=json.dumps(payload), headers=headers)
    info(f"request duration: {time.time() - st_time}")
    data = r.json()
    debug(data)
    return data

def place_sell_order(pair, price, quantity, order_type='limit', time_in_force="fok"):
    st_time = time.time()
    payload = {
        'clientOid': str(uuid.uuid4()),
        'side': 'sell',
        'type': order_type,
        'symbol': pair,
        'price': str(price),
        'size': str(quantity),
        'timeInForce': time_in_force
    }
    headers = create_headers(f'/{api_orders_endpoint}', 'POST', data_json=json.dumps(payload))
    r = requests.post(f'https://api.kucoin.com/{api_orders_endpoint}', data=json.dumps(payload), headers=headers)
    data = r.json()
    debug(data)
    info(f"request duration: {time.time() - st_time}")
    return data

def find_balance(balance, currency):
    currency_balance = list(filter(lambda x: x['currency'] == currency, balance['data']))
    if currency_balance:
        return currency_balance[0]
    else:
        return {} 

