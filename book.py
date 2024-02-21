from logbook import warn, info, debug, error, StreamHandler
from collections import deque
from operator import itemgetter
from tabulate import tabulate

class EmptyAskPriceException(Exception):
    pass

class Book():
    def __init__(self, pair, size=10):
        self.pair = pair
        self.size = size
        self.asks  = deque(maxlen=self.size)
        self.bids = deque(maxlen=self.size)

    def update(self, event):
        pair = "-".join(self.pair)
        if event['type'] == "message" and event['topic']  == f"/market/level2:{pair}":
            for tick in event['data']['changes']['asks']:
                self.update_asks([float(x) for x in tick])
            for tick in event['data']['changes']['bids']:
                self.update_bids([float(x) for x in tick])

    def update_asks(self, tick):
        self.asks.append(tick) 

    def update_bids(self, tick):
        self.bids.append(tick)

    @property
    def last_ask_price(self):
        try:
            return self.asks[0][0]
        except IndexError:
            raise EmptyAskPriceException

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

    def show(self):
        print(tabulate(self.asks))
        print(tabulate(self.bids))

    def is_full(self):
        return len(self.asks) == self.size and len(self.bids) == self.size
