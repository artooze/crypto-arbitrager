import urllib.request
import urllib.error
import urllib.parse
import json
from .market import Market
from lib.helpers import *

class BtccPro(Market):
    fix_marketdata_url = "http://localhost:8080/btcc/marketdata"

    def __init__(self, currency):
        super().__init__(currency)
        self.update_rate = 1

    def update_depth(self):
        try:
            self.update_depth_via_fix()
        except Exception as e:
            print("update_depth_via_fix Exception......")
            self.update_depth_via_rest()

    def update_depth_via_rest(self):
        url = 'https://pro-data.btcc.com/data/pro/orderbook?limit=5'
        req = urllib.request.Request(url, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})
        res = urllib.request.urlopen(req)
        depth = json.loads(res.read().decode('utf8'))
        self.depth = self.format_depth(depth)

    def update_depth_via_fix(self):
        res = requestGet(self.fix_marketdata_url)
        self.depth = {'asks': res['askOrders'], 'bids': res['bidOrders']}
