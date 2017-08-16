import urllib.request
import urllib.error
import urllib.parse
import json
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
    def __init__(self, currency, code):
        super().__init__(currency)
        self.update_rate = 20
        self.depth = {'asks': [{'price': 0, 'amount': 0}], 'bids': [
            {'price': 0, 'amount': 0}]}

    def update_depth(self):
        url = "https://api.bitfinex.com/v1/symbols_details"

        response = requests.request("GET", url)

        print(response.text)

        res = urllib.request.urlopen(
            'https://api.bitfinex.com/v1/book/bthbtc')
        jsonstr = res.read().decode('utf8')
        try:
            depth = json.loads(jsonstr)
        except Exception:
            logging.error("%s - Can't parse json: %s" % (self.name, jsonstr))
        self.depth = self.format_depth(depth)

if __name__ == "__main__":
    market = Bitfinex()
    print(market.get_ticker())
