import time
import base64
import hmac
import hashlib
import requests
import tomllib
import uuid
import json
from logbook import warn, info

api_secret = None
api_key = None
api_passphrase = None

def load_env():
    global api_key
    global api_secret
    global api_passphrase
    with open(".env.toml", "rb") as f:
        data = tomllib.load(f)
        credentials = data['credentials']
        api_key = credentials['key']
        api_secret = credentials['secret']
        api_passphrase = credentials['passphrase']

def create_headers(endpoint, method):
    now = int(time.time() * 1000)
    str_to_sign = str(now) + method + endpoint
    signature = base64.b64encode(hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
    passphrase = base64.b64encode(hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())

    headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": api_key,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2"
    }

    return headers

def get_balance():
    headers = create_headers('/api/v1/accounts', 'GET')
    response = requests.request('get', 'https://api.kucoin.com/api/v1/accounts', headers=headers)
    return response.json()


def place_buy_order(pair, price, quantity, order_type="fok"):
    headers = create_headers('/api/v1/orders', 'POST')
    payload = {
        'clientOid': str(uuid.uuid4()),
        'side': 'buy',
        'symbol': pair,
        'timeInForce': order_type
    }
    r = requests.post(f'https://api.kucoin.com/api/v1/orders', data=json.dumps(payload), headers=headers)
    data = r.json()
    warn(data)
    return data

def find_balance(balance, currency):
    currency_balance = list(filter(lambda x: x['currency'] == currency, balance['data']))
    if currency_balance:
        return currency_balance[0]
    else:
        return {} 

