from logbook import warn, info, debug, error, StreamHandler
import book
import account
import currencies
from logbook import warn, info, debug, error, StreamHandler
from enum import Enum

Result = Enum('Result', ['SUCCESS', 'FAILED'])


class Task():
    def __init__(self, pair, fund=0):
        self.pair = tuple(pair.split("-"))
        self.currencies = {}
        self.initialized = False
        self.buy = True
        self.book = book.Book(self.pair)
        self.buy_trade = False

    def init(self):
        info("dummy task: initialization ...")
        currency_1, currency_2 = self.pair
        self.currencies[currency_1] = {}
        self.currencies[currency_2] = {}

        self.currencies[currency_1]["detail"] = currencies.get_currency_detail(currency_1)['data']
        self.currencies[currency_2]["detail"] = currencies.get_currency_detail(currency_2)['data']

        self.update_balance()


    def update_balance(self):
        balance = account.get_balance()
        debug(balance)
        self.currencies[self.pair[0]]["balance"] = account.find_balance(balance, self.pair[0])
        self.currencies[self.pair[1]]["balance"] = account.find_balance(balance, self.pair[1])

    def sanitize_qty(self, qty):
        precision = self.currencies[self.pair[0]]["detail"]["precision"]
        return f"{qty:0.{precision}f}"

    def sanitize_price(self, price):
        return price

    def exec_buy(self, pair, price, qty, order_type="market"):
        price = self.sanitize_price(price)
        qty = self.sanitize_qty(qty)
        r = account.place_buy_order(pair, price, qty, order_type=order_type)
        if r['code'] != '200000':
            error(f"buy order - price: {price}, qty:{qty}")
            error(r)
            return Result.FAILED
        return Result.SUCESS

    def exec_sell(self, pair, price, qty, order_type="market"):
        price = self.sanitize_price(price)
        qty = self.sanitize_qty(qty)
        r = account.place_sell_order(pair, price, qty, order_type=order_type)
        if r['code'] != '200000':
            error(f"sell order - price: {price}, qty:{qty}")
            error(r)
            return Result.FAILED
        return Result.SUCESS

    async def run(self, event):
        debug(f"event received: {event}")
        self.book.update(event)

        
