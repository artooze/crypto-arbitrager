# Copyright (C) 2017, Philsong <songbohr@gmail.com>

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
import logging
import bitfinex
import traceback

# python3 arbitrage/arbitrage.py -m Bitfinex_BCH_BTC get-balance

class PrivateBitfinex_BCH_BTC(Market):
    def __init__(self, api_key = None, api_secret = None):
        super().__init__()

        self.trade_client = bitfinex.TradeClient(
                    api_key if api_key else config.Bitfinex_API_KEY,
                    api_secret if api_secret else config.Bitfinex_SECRET_TOKEN)

        self.currency = "BTC"
        self.symbol = 'bchbtc'

        self.get_info()
 
    def _buy(self, amount, price):
        """Create a buy limit order"""
        print("buy limit...")
        return
        res = self.trade_client.place_order(
            amount,
            price,
            'buy',
            'exchange limit',
            symbol=self.symbol)
        return res['order_id']

    def _sell(self, amount, price):
        """Create a sell limit order"""
        print("sell limit...")
        return
        res = self.trade_client.place_order(
            amount,
            price,
            'sell',
            'exchange limit',
            symbol=self.symbol)
        return res['order_id']

    def get_info(self):
        """Get balance"""
        res = self.trade_client.balances()
        print("req balances response:", res)

        for entry in res:
            if entry['type'] != 'exchange':
                continue

            currency = entry['currency'].upper()
            if currency not in (
                    'BTC', 'BCH'):
                continue

            if currency == 'BCH':
                self.bch_available = entry['available']
                self.bch_amount = entry['amount']

            elif currency == 'BTC':
                self.btc_available = entry['available']
                self.btc_amount = entry['amount']  
            
        