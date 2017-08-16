import logging
from .observer import Observer
import json
import time
import os
import math
import os, time
import sys
import traceback
import config
from private_markets import haobtccny, brokercny
from .marketmaker import MarketMaker
import threading

class HedgerBot(MarketMaker):
    exchange = 'HaobtcCNY'
    hedger = 'BrokerCNY'
    out_dir = 'hedger_history/'
    filename = exchange + '-bot.csv'

    def __init__(self):
        super().__init__()

        self.clients = {
            "HaobtcCNY": haobtccny.PrivateHaobtcCNY(config.HAOBTC_API_KEY, config.HAOBTC_SECRET_TOKEN),
            "BrokerCNY": brokercny.PrivateBrokerCNY(),
        }

        self.taker_fee = 0.002

        self.bid_fee_rate = config.bid_fee_rate
        self.ask_fee_rate = config.ask_fee_rate
        self.bid_price_risk = config.bid_price_risk
        self.ask_price_risk = config.ask_price_risk
        self.peer_exchange = self.hedger

        try:
            os.mkdir(self.out_dir)
        except:
            pass

        t = threading.Thread(target = self.msg_server)
        t.start()
        logging.info('HedgerBot Setup complete')
        # time.sleep(2)

    def process_message(self,message):
        kexchange = self.exchange

        try:
            message = message.decode('utf-8')
            message = json.loads(message)
            logging.info('msg:%s', message)
            type = message['type']
            price = message['price']

            logging.info('msg type:%s %s', type, price)

            if type == 'buy':
                buy_orders = self.get_orders('buy')
                buy_orders.sort(key=lambda x: x['price'], reverse=True)

                for buy_order in buy_orders:
                    if buy_order['price'] == price:
                        self.cancel_order(kexchange, 'buy', buy_order['id'])
                        break
            elif type == 'sell':
                sell_orders = self.get_orders('sell')
                sell_orders.sort(key=lambda x: x['price'])
                
                for sell_order in sell_orders:
                    if sell_order['price'] == price:
                        self.cancel_order(kexchange, 'sell', sell_order['id'])
                        break
        except Exception as e:
            logging.error("process message exception %s", e)
            traceback.print_exc()


    def market_maker(self, depths):
        # super().market_maker(depths)
        kexchange = self.exchange

        # update price
        try:
            bid_price = int(depths[self.exchange]["bids"][0]['price'])
            ask_price = int(depths[self.exchange]["asks"][0]['price'])
            bid_amount = (depths[self.exchange]["bids"][0]['amount'])
            ask_amount = (depths[self.exchange]["asks"][0]['amount'])
        except  Exception as ex:
            logging.warn("exception haobtc depths:%s" % ex)
            traceback.print_exc()
            bid_price = 0
            ask_price = 0
            bid_amount = 0
            ask_amount = 0

        try:
            peer_bid_price = int(depths[self.peer_exchange]["bids"][0]['price'])
            peer_ask_price = int(depths[self.peer_exchange]["asks"][0]['price'])

        except  Exception as ex:
            logging.warn("exception peer depths:%s" % ex)
            traceback.print_exc()
            return

        if peer_bid_price == 0 or peer_ask_price == 0:
            logging.warn("exception ticker")
            return

        if bid_price < 1:
            bid_price = 100
        if ask_price < 1:
            ask_price = 100000


        peer_bid_price = peer_bid_price*(1-self.taker_fee) - self.bid_price_risk
        peer_ask_price = peer_ask_price*(1+self.taker_fee) + self.ask_price_risk

        buyprice  = int(peer_bid_price) - 1
        sellprice = int(peer_ask_price) + 1

        min_buy_price = buyprice - config.MAKER_BUY_QUEUE*config.MAKER_BUY_STAGE
        max_sell_price = sellprice + config.MAKER_SELL_QUEUE*config.MAKER_SELL_STAGE

        self.buyprice_spread = set(range(min_buy_price+1, buyprice+1))
        self.sellprice_spread = set(range(sellprice, max_sell_price))

        logging.debug("%s/%s", self.sellprice_spread, self.buyprice_spread)

        self.buyprice = buyprice
        self.sellprice = sellprice

        # Update client balance
        self.update_balance()

        # query orders
        if self.is_buying():
            buy_orders = self.get_orders('buy')
            buy_orders.sort(key=lambda x: x['price'], reverse=True)
            buy_prices = [x['price'] for x in buy_orders]
            logging.debug(buy_prices)

            for buy_order in buy_orders:
                logging.debug(buy_order)
                result = self.clients[kexchange].get_order(buy_order['id'])
                logging.debug (result)
                if not result:
                    logging.warn("get_order buy #%s failed" % (buy_order['id']))
                    return

                self.hedge_order(buy_order, result)

                if result['status'] == 'CLOSE' or result['status'] == 'CANCELED':
                    self.remove_order(buy_order['id'])
                elif (result['price'] not in self.buyprice_spread):
                    logging.info("cancel buyprice %s result['price'] = %s" % (self.buyprice_spread, result['price']))
                    self.cancel_order(kexchange, 'buy', buy_order['id'])


        if self.is_selling():
            sell_orders = self.get_orders('sell')
            sell_orders.sort(key=lambda x: x['price'])
            sell_prices = [x['price'] for x in sell_orders]
            logging.debug(sell_prices)
            for sell_order in self.get_orders('sell'):
                logging.debug(sell_order)
                result = self.clients[kexchange].get_order(sell_order['id'])
                logging.debug (result)
                if not result:
                    logging.warn("get_order sell #%s failed" % (sell_order['id']))
                    return

                self.hedge_order(sell_order, result)

                if result['status'] == 'CLOSE' or result['status'] == 'CANCELED':
                    self.remove_order(sell_order['id'])
                elif (result['price'] not in self.sellprice_spread):
                    logging.info("cancel sellprice %s result['price'] = %s" % (self.sellprice_spread, result['price']))
                    self.cancel_order(kexchange, 'sell', sell_order['id'])
            
        # excute maker trade
        if config.MAKER_TRADE_ENABLE:
            if self.buying_len() < config.MAKER_BUY_QUEUE:
                self.new_order(kexchange, 'buy')
            if self.selling_len() < config.MAKER_SELL_QUEUE:
                self.new_order(kexchange, 'sell')

        # excute taker trade
        if config.TAKER_TRADE_ENABLE:
            taker_buy_price = peer_bid_price*(1-self.taker_fee)
            taker_sell_price = peer_ask_price*(1+self.taker_fee)

            logging.debug("price [%s,%s], peer [%s,%s] taker price:[%s,%s]", ask_price, bid_price, peer_ask_price, peer_bid_price, taker_buy_price, taker_sell_price)

            if ask_price!=0 and ask_price < taker_buy_price:
                if ask_amount < 0.1:
                    ask_amount = 0.1
                ask_amount+=0.01
                logging.info("to taker buy %s<%s", ask_price, taker_buy_price)
                self.new_order(kexchange, 'buy', maker_only=False, amount=ask_amount, price=ask_price)
                return

            if bid_price != 0 and bid_price > taker_sell_price:
                if bid_amount < 0.1:
                    bid_amount = 0.1
                bid_amount +=0.01
                logging.info("to taker sell %s>%s", bid_price, taker_sell_price)
                self.new_order(kexchange, 'sell', maker_only=False, amount= bid_amount, price=bid_price)
                return

    def get_sell_price(self):
        sell_orders = self.get_orders('sell')
        sell_prices = [x['price'] for x in sell_orders]
        price_candidate_set = set(self.sellprice_spread) - set(sell_prices)
        price_candidate_list = list(price_candidate_set)
        # price_candidate_list.sort()

        for x in price_candidate_list:
            return x

        return super().get_sell_price()

        logging.error (sell_orders)
        logging.error (sell_prices)
        logging.error (price_candidate_set)

    def get_buy_price(self):
        buy_orders = self.get_orders('buy')
        buy_prices = [x['price'] for x in buy_orders]

        price_candidate_set = set(self.buyprice_spread) - set(buy_prices)
        price_candidate_list = list(price_candidate_set)
        # price_candidate_list.sort(reverse=True)

        for x in price_candidate_list:
            return x
        
        return super().get_buy_price()

        logging.error(self.buyprice_spread)
        logging.error (buy_orders)
        logging.error (buy_prices)
        logging.error (price_candidate_set)

    def hedge_order(self, order, result):
        if result['deal_size'] <= 0:
            logging.debug("[hedger]NOTHING TO BE DEALED.")
            return

        order_id = result['order_id']        
        deal_size = result['deal_size']
        price = result['avg_price']

        amount = deal_size - order['deal_amount']
        if amount <= config.broker_min_amount:
            logging.debug("[hedger]deal nothing while.")
            return

        maker_only = order['maker_only']
        client_id = str(order_id) + '-' + str(order['deal_index'])+('' if maker_only else '-taker')

        logging.info("hedge new deal: %s", result)
        hedge_side = 'SELL' if result['side'] =='BUY' else 'BUY'
        logging.info('hedge [%s] to broker: %s %s %s', client_id, hedge_side, amount, price)

        if hedge_side == 'SELL':
            self.clients[self.hedger].sell(amount, price, client_id)
        else:
            self.clients[self.hedger].buy(amount, price, client_id)

        # update the deal_amount of local order
        self.remove_order(order_id)
        order['deal_amount'] = deal_size
        order['deal_index'] +=1
        self.orders.append(order)
        
