# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .market import Market, TradeException
import time
import base64
import hmac
import urllib.request
import urllib.parse
import urllib.error
import hashlib
import sys
import json
import config
from lib.helpers import *


class PrivateBtccProCNY(Market):
    balance_url = "http://localhost:8080/btcc/account"
    buy_url = "http://localhost:8080/btcc/buy"
    sell_url = "http://localhost:8080/btcc/sell"

    def __init__(self):
        super().__init__()
        self.currency = "CNY"
        self.get_info()

    def _buy(self, amount, price):
        """Create a buy limit order"""
        print("buy...")
        params = {"amount": amount, "price": price}
        return requestPost(self.buy_url, params)

        response = httpPost(self.buy_url, params)
        if not response:
            raise TradeException("buy failed")

    def _sell(self, amount, price):
        """Create a sell limit order"""
        print("sell...")

        params = {"amount": amount, "price": price}
        return requestPost(self.sell_url, params)

        response = httpPost(self.sell_url, params)
        if not response:
            raise TradeException("sell failed")

    def get_info(self):
        """Get balance"""
        response = requestGet(self.balance_url)
        # print("btccpro get_info response:", response)
        if response:
            # self.btc_balance = float(response["UsableMargin"])
            self.cny_balance = float(response["UsableMargin"])
            # todo:
            self.sell_frozen = float(response["TotalSellSize1"])
            self.buy_frozen = float(response["TotalBuySize1"])
            