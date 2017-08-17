# Copyright (C) 2017, Philsong <songbohr@gmail.com>

from ._bitfinex import Bitfinex

class Bitfinex_BTC_USD(Bitfinex):
    def __init__(self):
        super().__init__("USD", "BTC", "btcusd")

