# Copyright (C) 2017, Philsong <songbohr@gmail.com>

from ._bitfinex import Bitfinex


# https://api.bitfinex.com/v1/symbols_details
#   {
#     "pair": "bchbtc",
#     "price_precision": 5,
#     "initial_margin": "30.0",
#     "minimum_margin": "15.0",
#     "maximum_order_size": "2000.0",
#     "minimum_order_size": "0.001",
#     "expiration": "NA"
#   },

class Bitfinex_BCH_BTC(Bitfinex):
    def __init__(self):
        super().__init__("BTC", "BCH", "bchbtc")

if __name__ == "__main__":
    market = Bitfinex_BCH_BTC()
    print(market.get_ticker())
