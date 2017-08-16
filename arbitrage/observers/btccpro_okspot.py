import logging
import config
import time
from .observer import Observer
from .emailer import send_email
from fiatconverter import FiatConverter
from private_markets import okcoincny,btccprocny
import os, time
import sys
import traceback
from .basicbot import BasicBot

# python3 arbitrage/arbitrage.py -oBTCCPro_OkSpot -mBtccProCNY,OKCoinCNY

class BTCCPro_OkSpot(BasicBot):
    exchange = 'BtccProCNY'
    hedger = 'OKCoinCNY'

    def __init__(self):
        super().__init__()

        self.clients = {
            "OKCoinCNY": okcoincny.PrivateOkCoinCNY(config.OKCOIN_API_KEY, config.OKCOIN_SECRET_TOKEN),
            "BtccProCNY": btccprocny.PrivateBtccProCNY(),
        }

        self.trade_wait = config.trade_wait  # in seconds
        self.last_trade = 0

        self.init_btc = {'OKCoinCNY':500, 'BtccProCNY':500}
        self.init_cny = {'OKCoinCNY':100, 'BtccProCNY':100}

        self.spread = 0.1

        self.simluate = True

        t = threading.Thread(target = self.msg_server)
        t.start()
        logging.info('BTCCPro_OkSpot Setup complete')
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


    def hedgeALG1(self, depths):
        # update price
        try:
            bid_price = (depths[self.exchange]["bids"][0]['price'])
            ask_price =  (depths[self.exchange]["asks"][0]['price'])
            bid_amount = int(depths[self.exchange]["bids"][0]['amount'])
            ask_amount=  int(depths[self.exchange]["asks"][0]['amount'])

            hedger_bid_price = (depths[self.hedger]["bids"][0]['price'])
            hedger_ask_price =  (depths[self.hedger]["asks"][0]['price'])
            hedger_bid_amount = (depths[self.hedger]["bids"][0]['amount'])
            hedger_ask_amount = (depths[self.hedger]["asks"][0]['amount'])

        except  Exception as ex:
            logging.warn("exception depths:%s" % ex)
            traceback.print_exc()
            return

        if bid_price == 0 or ask_price == 0 or hedger_bid_price == 0 or hedger_ask_price == 0:
            logging.info("exception ticker %s %s %s %s", bid_price ,ask_price,hedger_bid_price,hedger_ask_price)
            return

        # 并行程序一
        # 当BTCC价格（BTCC买一）减去OKCOIN的价格（OKCOIN卖一）大于-2时，买X个OKCOIN现货（价格为卖一价+0.1元方便成交），
        # 卖出X个BTCC现货（X数量为BTCC买一的数量）


        # 并行程序二
        # 当BTCC价格减去OKCOIN的价格小于-8时，卖Y个OKCOIN现货（买一价-0.1元），买入Y个BTCC现货 （Y数量为BTCC卖一的数量）


        # -2 -8 0.1 这三个值将来为变量


        # Update client balance
        self.update_balance()

        logging.info("maker:%s %s %s %s", bid_price, bid_amount, ask_price, ask_amount)
        logging.info("hedger:%s %s %s %s", hedger_bid_price, hedger_bid_amount, hedger_ask_price, hedger_ask_amount)

        logging.info("bid_price - hedger_ask_price=%0.2f", bid_price - hedger_ask_price)
        logging.info("ask_price - hedger_bid_price=%0.2f", ask_price - hedger_bid_price)

        current_time = time.time()
        if current_time - self.last_trade < self.trade_wait:
            logging.warn("Can't automate this trade, last trade " +
                         "occured %.2f seconds ago" %
                         (current_time - self.last_trade))
            return

        if bid_price - hedger_ask_price > -2:

            hedge_amount = int(min(bid_amount, 1))
            if hedge_amount < 1:
                logging.warn("sell in btcc %s , buy in ok %s ..too small [%s]btc", bid_price, hedger_ask_price, hedge_amount)
                return
            
            btc_balance = int(self.clients[self.exchange].cny_balance/(bid_price-self.spread))
            if btc_balance < hedge_amount:
                logging.warn("btcc btc balance %s insufficent", btc_balance)
                return

            if self.clients[self.hedger].cny_balance < hedge_amount*(hedger_ask_price+self.spread):
                logging.warn("okcoin cny balance %s insufficent", self.clients[self.hedger].cny_balance )
                return       

            logging.info("sell in btcc %s , buy in ok %s [%s]btc", bid_price, hedger_ask_price, hedge_amount)

            if not self.simluate:
                self.new_order(self.exchange, 'sell', maker_only=False, amount=hedge_amount, price=bid_price-self.spread)
                self.new_order(self.hedger, 'buy', maker_only=False, amount=hedge_amount, price=hedger_ask_price+self.spread)
                
            self.last_trade = time.time()

        elif ask_price - hedger_bid_price < -8 :
            hedge_amount = int(min(ask_amount, 1))
            if hedge_amount < 1:
                logging.warn("sell in ok %s, buy in btcc %s ..insufficent [%s]btc", ask_price, hedger_bid_price, hedge_amount)
                return

            btc_balance = int(self.clients[self.exchange].cny_balance/(ask_price+self.spread))
            if btc_balance < hedge_amount:
                logging.warn("btcc cny balance %s insufficent", btc_balance)
                return

            if self.clients[self.hedger].btc_balance < hedge_amount:
                logging.warn("okcoin btc balance %s insufficent", self.clients[self.hedger].btc_balance )
                return       
                
            logging.info("sell in ok %s, buy in btcc %s [%s]btc", ask_price, hedger_bid_price, hedge_amount)
            
            if not self.simluate:
                self.new_order(self.exchange, 'buy', maker_only=False, amount=hedge_amount, price=ask_price+self.spread)
                self.new_order(self.hedger, 'sell', maker_only=False, amount=hedge_amount, price=hedger_ask_price-self.spread)
                
            self.last_trade = time.time()


    def update_trade_history(self, time, price, cny, btc):
        filename = self.out_dir + self.filename
        need_header = False

        if not os.path.exists(filename):
            need_header = True

        fp = open(filename, 'a+')

        if need_header:
            fp.write("timestamp, price, cny, btc\n")

        fp.write(("%d") % time +','+("%.2f") % price+','+("%.2f") % cny+','+ str(("%.4f") % btc) +'\n')
        fp.close()

    def update_balance(self):
        for kclient in self.clients:
            self.clients[kclient].get_info()

    def begin_opportunity_finder(self, depths):
        self.hedgeALG1(depths)

    def end_opportunity_finder(self):
        pass

    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc, weighted_buyprice, weighted_sellprice):
        pass
