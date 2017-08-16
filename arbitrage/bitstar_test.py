#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import decimal

from lib.bitstar_sdk import ApiClient
import config

API_KEY = config.BITSTAR_API_KEY
API_SECRET = config.BITSTAR_SECRET_TOKEN

def main():
    client = ApiClient(API_KEY, API_SECRET)

    # 用户主资产信息
    # currency 数字货币币种代号  btc 　比特币   eth 　以太坊
    main_account = client.get_main_account('btc')
    print(main_account)

    # 用户子账号信息（合约资产）
    # contractCode 合约类型代号  swap-btc 　比特币现货合约  swap-eth 　以太坊现货合约
    sub_account = client.get_sub_account('swap-btc')
    print(sub_account)

    # 主资产向子账号转入
    transfer_sub = client.transfer_to_sub('swap-btc', decimal.Decimal('0.02'))
    print(transfer_sub)

    # 子账号向主资产转出
    transfer_main = client.transfer_to_main('swap-btc', decimal.Decimal('0.01'))
    print(transfer_main)

    # 下单
    # businessType 业务类型代码  swap-btc-cny　 比特币对人民币现货合约   swap-eth-cny　 以太坊对人民币现货合约
    # tradeType 交易类型    1 开多 　2 开空　 3 平多　 4 平空
    # price 只保留一位有效小数
    # amount 数量是人民币的数量，100的整数倍
    trade = client.trade('swap-btc-cny', 2, decimal.Decimal('18300.1'), 100)
    print(trade)

    order_id = trade['orderid']

    # 撤销订单
    cancel = client.cancel('swap-btc-cny', order_id)
    print(cancel)

    # 查看单个订单信息
    order_info = client.order_info('swap-btc-cny', order_id)
    print(order_info)

    # 查看委托中订单信息
    orders_in = client.order_in_list('swap-btc-cny')
    print(orders_in)

    # 查看最近完成订单信息
    orders_over = client.order_over_list('swap-btc-cny')
    print(orders_over)

    # 查看持仓信息
    storeinfo = client.storeinfo('swap-btc-cny')
    print(storeinfo)

    publicinfo = client.publicinfo('swap-btc-cny')
    print(publicinfo)

if __name__ == '__main__':
    main()
