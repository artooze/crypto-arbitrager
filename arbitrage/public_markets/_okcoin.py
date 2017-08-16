import urllib.request
import urllib.error
import urllib.parse
import json
from .market import Market
import config
class OKCoin(Market):
    def __init__(self, currency, code):
        super().__init__(currency)
        self.code = code
        self.update_rate = 1
        self.event = 'okcoin_depth'
        self.subscribe_depth()

    def update_depth(self):
        url = "https://www.okcoin.cn/api/v1/depth.do?symbol=" + self.code
        req = urllib.request.Request(url, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})
        res = urllib.request.urlopen(req)
        depth = json.loads(res.read().decode('utf8'))
        self.depth = self.format_depth(depth)
