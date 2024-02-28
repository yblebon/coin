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
    MISSING_EXCHANGE_TIMESTAMP = auto()

@dataclass
class Currency:
    exchange: str
    name: str
    qty_step: float = None
    price_precision: float = None

    def __post_init__(self):
        self.exchange = self.exchange.upper()
        self.name = self.name.upper()

    def __repr__(self) -> str:
        return f"{self.exchange}__{self.name}"
    
    def __str__(self) -> str:
        return f"{self.exchange}__{self.name}"

    
@dataclass
class Tick:
    exchange: str
    base: Currency
    quote: Currency
    price: float
    qty: float
    side: Side
    exchange_ts: float = None
    created_ts: float = time.time()

    def __post_init__(self):
        pass

    def is_ask(self):
        return self.side == Side.SELL
    
    def is_bid(self):
        return self.side == Side.BUY
    
    def get_date(self):
        return datetime.fromtimestamp(self.exchange_ts)
    
    def get_ts(self):
        return self.ts
    
    @property
    def latency(self):
        return self.created_ts - self.exchange_ts

    def is_correct(self):
        if self.latency < 0:
            return Anomaly.WRONG_LATENCY
        elif self.price <= 0:
            return Anomaly.WRONG_PRICE
        elif self.qty <= 0:
            return Anomaly.WRONG_QTY
        return True
    
    def __repr__(self) -> str:
        return f"{self.exchange}__{self.base.name}_{self.quote.name}"
    
    def __str__(self) -> str:
        return f"{self.exchange}__{self.base.name}_{self.quote.name}"


if __name__ == "__main__":
    b = Currency('EXCHANGE', 'btc')
    q = Currency('EXCHANGE', 'usdt')
    print(b)
    t = Tick('EXCHANGE', b, q, -56.23, 45.45, Side.BUY, exchange_ts=1709128420.8183336)
    print(t)
    print(t.is_bid())
    print(t.get_date())
    print(t.latency)
    print (t.is_correct())

