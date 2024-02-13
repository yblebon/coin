import time
import base64
import hmac
import hashlib
import requests

def get_balance(api_key, api_secret, api_passphrase):
    url = 'https://api.kucoin.com/api/v1/accounts'
    now = int(time.time() * 1000)
    str_to_sign = str(now) + 'GET' + '/api/v1/accounts'
    signature = base64.b64encode(hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
    passphrase = base64.b64encode(hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())

    headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": api_key,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2"
    }

    response = requests.request('get', url, headers=headers)
    return response.json()


def find_balance(balance, currency):
    currency_balance = list(filter(lambda x: x['currency'] == currency, balance['data']))
    if currency_balance:
        return currency_balance[0]
    else:
        return {} 

