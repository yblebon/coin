from typing import NamedTuple
from enum import Enum, auto
import time
from datetime import datetime

class Side(Enum):
    BUY = auto()
    SELL = auto()

class Anomaly(Enum):
    WRONG_PRICE = auto()
    WRONG_QTY = auto()
    WRONG_LATENCY = auto()
    

class Tick(NamedTuple):
    exchange: str
    pair: str
    price: float
    qty: float
    side: Side
    ts: float = time.time()
    created_ts: float = time.time()

    def is_ask(self):
        return self.side == Side.SELL
    
    def is_bid(self):
        return self.side == Side.BUY
    
    def get_date(self):
        return datetime.fromtimestamp(self.ts)
    
    def get_ts(self):
        return self.ts
    
    @property
    def latency(self):
        return self.created_ts - self.ts

    def is_correct(self):
        if self.latency < 0:
            return Anomaly.WRONG_LATENCY
        elif self.price <= 0:
            return Anomaly.WRONG_PRICE
        elif self.qty <= 0:
            return Anomaly.WRONG_QTY
        return True


if __name__ == "__main__":
    t = Tick('exchange', 'btc-usdt', -56.23, 45.45, Side.BUY, ts=1709128420.8183336)
    print(t)
    print(t.is_bid())
    print(t.get_date())
    print(t.latency)
    print (t.is_correct())

