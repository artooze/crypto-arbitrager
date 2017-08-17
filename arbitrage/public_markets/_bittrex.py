# Copyright (C) 2017, Philsong <songbohr@gmail.com>

import logging
import requests
from bittrex import bittrex
from .market import Market


# https://bittrex.com/api/v1.1/public/getorderbook?market=BTC-BCC&type=both
# {
#   "success": true,
#   "message": "",
#   "result": {
#     "buy": [
#       {
#         "Quantity": 96.83510777,
#         "Rate": 0.07303001
#       },
#       {
#       }
#     ],
#     "sell": [
#       {
#         "Quantity": 30.70354481,
#         "Rate": 0.07303002
#       },
#       {
#       }
#     ]
#   }
# }

class Bittrex(Market):
    def __init__(self, base_currency, market_currency, pair_code):
        super().__init__(base_currency, market_currency, pair_code)

        self.client = bittrex.Bittrex('','')

    def update_depth(self):
        raw_depth = self.client.get_orderbook(self.pair_code, 'both')
        self.depth = self.format_depth(raw_depth)

    # override method
    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x['Rate']), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i['Rate']), 'amount': float(i['Quantity'])})
        return r

    # override method
    def format_depth(self, depth):
        bids = self.sort_and_format(depth['result']['buy'], True)
        asks = self.sort_and_format(depth['result']['sell'], False)
        return {'asks': asks, 'bids': bids}
