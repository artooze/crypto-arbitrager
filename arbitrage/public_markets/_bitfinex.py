# Copyright (C) 2017, Philsong <songbohr@gmail.com>

import logging
import requests
from .market import Market

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

class Bitfinex(Market):
    def __init__(self, base_currency, market_currency, pair_code):
        super().__init__(base_currency, market_currency, pair_code)

    def update_depth(self):
        url = 'https://api.bitfinex.com/v1/book/%s' % self.pair_code
        response = requests.request("GET", url, timeout=self.request_timeout)
        raw_depth = response.json()

        self.depth = self.format_depth(raw_depth)

    # override method
    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x['price']), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i['price']), 'amount': float(i['amount'])})
        return r

