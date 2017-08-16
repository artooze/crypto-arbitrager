# Copyright (C) 2017, Philsong <songbohr@gmail.com>

import urllib.request
import urllib.error
import urllib.parse
import json
from .market import Market
import lib.bitstar_sdk as ApiClient

class BS_StandardCNY(Market):
    def __init__(self):
        super().__init__('CNY')
        self.update_rate = 1
        self.client = ApiClient('', '')

    def update_depth(self):
        depth = {}
        try:
            publicinfo = self.client.publicinfo()
            print(publicinfo)
            depth['asks'] = [[publicinfo.standardprice, 1]]
            depth['bids'] = [[publicinfo.standardprice, 1]]
        except Exception as e:
            return

        self.depth = self.format_depth(depth)
