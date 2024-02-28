from dataclasses import dataclass
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

@dataclass
class Currency:
    exchange: str
    name: str
    qty_step: float = None
    price_precision: float = None

    def __post_init__(self):
        self.exchange = self.exchange.upper()
        self.name = self.name.upper()

    
@dataclass
class Tick:
    quote: Currency
    base: Currency
    price: float
    qty: float
    side: Side
    ts: float = time.time()
    created_ts: float = time.time()

    def __post_init__(self):
        pass

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
    b = Currency('EXCHANGE', 'btc')
    q = Currency('EXCHANGE', 'usdt')
    t = Tick(b, q, -56.23, 45.45, Side.BUY, ts=1709128420.8183336)
    print(t)
    print(t.is_bid())
    print(t.get_date())
    print(t.latency)
    print (t.is_correct())

