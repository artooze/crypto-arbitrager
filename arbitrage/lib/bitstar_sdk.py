#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import decimal
import hashlib
import json

import requests


class Dict(dict):
    def __init__(self, **kw):
        super().__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


def _toDict(d):
    return Dict(**d)


class ApiClient(object):
    # timeout in 5 seconds:
    timeout = 5
    api_url = 'https://www.bitstar.com'
    api_version = '/api/v1'

    def __init__(self, appKey, appSecret):
        self._accessKeyId = appKey
        self._accessKeySecret = appSecret  # change to bytes

    def get_main_account(self, currency: str):
        """
        用户主资产信息
        https://github.com/bitstarcom/BitStar-API/wiki/%E7%94%A8%E6%88%B7%E4%B8%BB%E8%B5%84%E4%BA%A7%E4%BF%A1%E6%81%AF
        :param currency:
        :return:
        """
        uri = '/fund/mainAccount/%s' % (currency,)
        return self._call(uri)

    def get_sub_account(self, contract_code: str):
        """
        用户子账号信息（合约资产）
        https://github.com/bitstarcom/BitStar-API/wiki/%E7%94%A8%E6%88%B7%E5%AD%90%E8%B4%A6%E5%8F%B7%E4%BF%A1%E6%81%AF%EF%BC%88%E5%90%88%E7%BA%A6%E8%B5%84%E4%BA%A7%EF%BC%89
        :param contract_code:
        :return:
        """
        uri = '/fund/subAccount/%s' % (contract_code,)
        return self._call(uri)

    def transfer_to_sub(self, contract_code: str, amount: decimal.Decimal):
        """
        主资产向子账号转入
        https://github.com/bitstarcom/BitStar-API/wiki/%E4%B8%BB%E8%B5%84%E4%BA%A7%E5%90%91%E5%AD%90%E8%B4%A6%E5%8F%B7%E8%BD%AC%E5%85%A5
        :param contract_code:
        :param amount:
        :return:
        """
        uri = '/fund/transferToSub/%s/%s' % (contract_code, amount)
        return self._call(uri)

    def transfer_to_main(self, contract_code: str, amount: decimal.Decimal):
        """
        子账号向主资产转出
        https://github.com/bitstarcom/BitStar-API/wiki/%E5%AD%90%E8%B4%A6%E5%8F%B7%E5%90%91%E4%B8%BB%E8%B5%84%E4%BA%A7%E8%BD%AC%E5%87%BA
        :param contract_code:
        :param amount:
        :return:
        """
        uri = '/fund/transferToMain/%s/%s' % (contract_code, amount)
        return self._call(uri)

    def trade(self, business_type: str, trade_type: int, price: decimal.Decimal, amount: int):
        """
        下单
        https://github.com/bitstarcom/BitStar-API/wiki/%E4%B8%8B%E5%8D%95
        :param business_type:
        :param trade_type:
        :param price:
        :param amount:
        :return:
        """
        uri = '/trade/order/%s/%s/%s/%s' % (business_type, trade_type, price, amount)
        return self._call(uri)

    def cancel(self, business_type: str, order_id: int):
        """
        撤销订单
        https://github.com/bitstarcom/BitStar-API/wiki/%E6%92%A4%E9%94%80%E8%AE%A2%E5%8D%95
        :param order_id:
        :return:
        """
        uri = '/trade/cancel/%s/%s' % (business_type, order_id)
        return self._call(uri)

    def order_info(self, business_type: str, order_id: int):
        """
        查看单个订单信息
        https://github.com/bitstarcom/BitStar-API/wiki/%E6%9F%A5%E7%9C%8B%E5%8D%95%E4%B8%AA%E8%AE%A2%E5%8D%95%E4%BF%A1%E6%81%AF
        :param business_type:
        :param order_id:
        :return:
        """
        uri = '/trade/orderinfo/%s/%s' % (business_type, order_id)
        return self._call(uri)

    def order_in_list(self, busiess_type: str):
        """
        查看委托中订单信息
        https://github.com/bitstarcom/BitStar-API/wiki/%E6%9F%A5%E7%9C%8B%E5%A7%94%E6%89%98%E4%B8%AD%E8%AE%A2%E5%8D%95%E4%BF%A1%E6%81%AF
        :param busiess_type:
        :return:
        """
        uri = '/trade/orders_in/%s' % (busiess_type,)
        return self._call(uri)

    def order_over_list(self, busiess_type: str):
        """
        查看最近完成订单信息
        https://github.com/bitstarcom/BitStar-API/wiki/%E6%9F%A5%E7%9C%8B%E6%9C%80%E8%BF%91%E5%AE%8C%E6%88%90%E8%AE%A2%E5%8D%95%E4%BF%A1%E6%81%AF
        :param busiess_type:
        :return:
        """
        uri = '/trade/orders_over/%s' % (busiess_type,)
        return self._call(uri)

    def storeinfo(self, busiess_type: str):
        """
        查看持仓信息
        https://github.com/bitstarcom/BitStar-API/wiki/%E6%9F%A5%E7%9C%8B%E6%8C%81%E4%BB%93%E4%BF%A1%E6%81%AF
        :param busiess_type:
        :return:
        """
        uri = '/trade/storeinfo/%s' % (busiess_type,)
        return self._call(uri)

    def publicinfo(self, busiess_type: str):
        """
        查看持仓信息
        https://github.com/bitstarcom/BitStar-API/wiki/%E6%9F%A5%E7%9C%8B%E6%8C%81%E4%BB%93%E4%BF%A1%E6%81%AF
        :param busiess_type:
        :return:
        """
        uri = '/market/publickinfo/%s' % (busiess_type,)
        return self._get(uri)

    def _call(self, uri):
        sign_uri = self.api_version + uri + '/' + self._accessKeySecret
        md5 = hashlib.md5()
        md5.update(sign_uri.encode('utf-8'))
        sign = md5.hexdigest()
        params = {
            'accessKey': self._accessKeyId,
            'signData': sign
        }
        req_url = self.api_url + self.api_version + uri
        resp = requests.post(url=req_url, data=params, timeout=self.timeout)
        return self._parse(resp.text)

    def _parse(self, text):
        result = json.loads(text, object_hook=_toDict)
        if 'error' not in result:
            return result
        raise ApiError('%s' % (text))

    def _get(self, uri, params = None):
        req_url = self.api_url + self.api_version + uri
        resp = requests.get(url=req_url, params=params, timeout=self.timeout)
        return self._parse(resp.text)

class ApiError(BaseException):
    pass
