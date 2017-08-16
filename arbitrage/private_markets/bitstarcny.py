# Copyright (C) 2016, Philsong <songbohr@gmail.com>

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
from lib.bitstar_sdk import ApiClient
import logging

class PrivateBitstarCNY(Market):
    def __init__(self, API_KEY = None, API_SECRET = None):
        super().__init__()
    
        self.market = ApiClient(API_KEY, API_SECRET)

        self.currency = "CNY"
        self.get_info()

    def _trade(self, amount, price, is_long=True):
        """Create a buy limit order"""
        tradeType = 1
        #　1 开多 　2 开空　 3 平多　 4 平空
        if is_long:
            tradeType = 2

        try:
            cny_amount = (amount*price)//100*100
            trade = client.trade('swap-btc-cny', tradeType, decimal.Decimal(price), cny_amount)
        except expression as identifier:
            pass

        if trade and trade['result'] == 0:
            return trade['orderid']

        return False

    def _buy(self, amount, price):
        return self._trade(amount, price, is_long=True)

    def _sell(self, amount, price):
        """Create a sell limit order"""
        return self._trade(amount, price, is_long=False)


    def _get_order(self, order_id):
        order_info = self.market.order_info('swap-btc-cny', order_id)

        if not response:
            return response

        if "error_code" in response:
            logging.warn (response)
            return False

        order = response['orders'][0]
        resp = {}
        resp['order_id'] = order['order_id']
        resp['amount'] = order['amount']
        resp['price'] = order['price']
        resp['deal_size'] = order['deal_amount']
        resp['avg_price'] = order['avg_price']

        status = order['status']
        if status == -1:
            resp['status'] = 'CANCELED'
        elif status == 2:
            resp['status'] = 'CLOSE'
        else:
            resp['status'] = 'OPEN'
        return resp

    def _cancel_order(self, order_id):
        response = self.market.cancel(order_id)

        if not response:
            return response

        if response and "error_code" in response:
            logging.warn (response)
            return False
            
        if response['result'] == True:
            return True
        else:
            return False

    def get_info(self):
        """Get balance"""
        response = self.market.accountInfo()
        if response:
            if "error_code" in response:
                logging.warn(response)
                return False
            else:
                self.btc_balance = float(response['info']['funds']['free']['btc'])
                self.cny_balance = float(response['info']['funds']['free']['cny'])
                self.btc_frozen =  float(response['info']['funds']['freezed']['btc'])
                self.cny_frozen =  float(response['info']['funds']['freezed']['cny'])
        return response
        