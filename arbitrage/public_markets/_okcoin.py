# Copyright (C) 2017, Philsong <songbohr@gmail.com>

import urllib.request
import urllib.error
import urllib.parse
import json
import config
from .market import Market

class OKCoin(Market):
    def __init__(self, base_currency, market_currency, pair_code):
        super().__init__(base_currency, market_currency, pair_code)
        
        self.event = 'okcoin_depth'
        self.subscribe_depth()

    def update_depth(self):
        url = "https://www.okcoin.cn/api/v1/depth.do?symbol=" + self.pair_code
        req = urllib.request.Request(url, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})
        res = urllib.request.urlopen(req)
        depth = json.loads(res.read().decode('utf8'))
        self.depth = self.format_depth(depth)
