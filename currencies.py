import requests
from logbook import warn, info, debug, error

def get_currency_detail(currency):
    r = requests.get(f'https://api.kucoin.com/api/v3/currencies/{currency}')
    data = r.json()
    debug(data)
    return data
