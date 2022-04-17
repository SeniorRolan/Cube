import requests
import base64
import codecs
import datetime
import hashlib
import hmac
import json
import urllib.parse
from time import time
from typing import Tuple, List, Dict
import ujson


class Coinsbit_API(object):
    def __init__(self, pr_key: str, pub_key: str):

        self.pr_key = pr_key
        self.pub_key = pub_key

        #Base url
        self.BASE_URL = 'https://coinsbit.io'

        #Current market endpoints
        self.CURRENT_ORDER_BOOK_ENDPOINT = '/api/v1/public/book'
        self.CURRENT_BALANCES_ENDPOINT = "/api/v1/account/balances"
        self.CURRENT_TRANSACTIONS_ENDPOINT = '/api/v1/account/trades'
        self.ORDERS_IN_MARKET_ENDPOINT = '/api/v1/orders'
        self.ORDERS_HISTORY_ENDPOINT = '/api/v1/account/order_history'
        self.TRANSACTIONS_HISTORY_ENDPOINT = '/api/v1/public/history'
        self.PLACE_ORDER_ENDPOINT = '/api/v1/order/new'
        self.CANCEL_ORDER_ENDPOINT = '/api/v1/order/cancel'
        pass

    def current_order_book(self, tickers: list, limit: int = 50, offset: int = 0)-> List[dict]:
        """
        Gets currencies codes to build currencyPairCode, prepares exchange request
        and returns current asks and bids.
        """
        tickers = [ticker.upper() for ticker in tickers]
        currency_pair_code = tickers[0] + "_" + tickers[1]
        request_url = self.BASE_URL + self.CURRENT_ORDER_BOOK_ENDPOINT
        request_body = f"?market={currency_pair_code}&side=sell&offset={offset}&limit={limit}"

        result = requests.get(request_url+request_body)
        return result.text

    def current_transactions(self, orderId: str, offset: int = 0, limit: int = 50):
        data = {
            "request": self.CURRENT_TRANSACTIONS_ENDPOINT,
            "nonce": str(time() * 1000),
        }
        payload = base64.b64encode(ujson.dumps(data, escape_forward_slashes=False).encode('utf-8'))
        signature = hmac.new(self.pr_key.encode("utf-8"), payload, hashlib.sha512).hexdigest()
        headers = {
            "Content-type": "application/json",
            "X-TXC-APIKEY": self.pub_key,
            "X-TXC-PAYLOAD": payload,
            "X-TXC-SIGNATURE": signature
        }
        request_url = self.BASE_URL + self.CURRENT_TRANSACTIONS_ENDPOINT
        params = {"orderId": orderId,
                  "offset": offset,
                  "limit": limit}
        request_msg = request_url

        current_transactions_result = requests.post(request_msg, headers=headers, params=params, data=codecs.escape_encode(ujson.dumps(data, escape_forward_slashes=False).encode("utf8"))[0])
        if current_transactions_result.status_code != 204:
            return current_transactions_result.text


    def current_balances(self, currency: str):
        data = {
            "request": self.CURRENT_BALANCES_ENDPOINT,
            "nonce": str(time() * 1000),
        }
        payload = base64.b64encode(ujson.dumps(data, escape_forward_slashes=False).encode('utf-8'))
        signature = hmac.new(self.pr_key.encode("utf-8"), payload, hashlib.sha512).hexdigest()
        headers = {
            "Content-type": "application/json",
            "X-TXC-APIKEY": self.pub_key,
            "X-TXC-PAYLOAD": payload,
            "X-TXC-SIGNATURE": signature
        }
        request_url = self.BASE_URL + self.CURRENT_BALANCES_ENDPOINT
        params = {"currency": currency}
        current_balances_result = requests.post(request_url, headers=headers, params=params, data=codecs.escape_encode(ujson.dumps(data, escape_forward_slashes=False).encode("utf8"))[0])
        return current_balances_result.text.encode('utf-8')

    def orders_in_market(self, tickers: list, offset: int = 0, limit: int = 50):
        data = {
            "request": self.ORDERS_IN_MARKET_ENDPOINT,
            "nonce": str(time() * 1000),
        }
        # request_data_bytes, _ = codecs.escape_encode(json.dumps(data).encode('utf-8'))
        # print(_)
        # print(request_data_bytes)
        payload = base64.b64encode(ujson.dumps(data, escape_forward_slashes=False).encode('utf-8'))
        signature = hmac.new(self.pr_key.encode("utf-8"), payload, hashlib.sha512).hexdigest()
        headers = {
            "Content-type": "application/json",
            "X-TXC-APIKEY": self.pub_key,
            "X-TXC-PAYLOAD": payload,
            "X-TXC-SIGNATURE": signature
        }
        request_url = self.BASE_URL + self.ORDERS_IN_MARKET_ENDPOINT
        tickers = [ticker.upper() for ticker in tickers]
        currency_pair_code = tickers[0] + "_" + tickers[1]
        params = {
            'market': currency_pair_code,
            'offset': offset,
            'limit': limit,
        }
        orders_in_market_result = requests.post(request_url, headers=headers, params=params, data=codecs.escape_encode(ujson.dumps(data, escape_forward_slashes=False).encode("utf8"))[0])
        return orders_in_market_result.text

    def txs_history(self, tickers: list, lastId: int, limit: int = 50):

        request_url = self.BASE_URL + self.TRANSACTIONS_HISTORY_ENDPOINT
        tickers = [ticker.upper() for ticker in tickers]
        currency_pair_code = tickers[0] + "_" + tickers[1]
        params = {
            'market': currency_pair_code,
            'lastId': lastId,
            'limit': limit
        }
        txs_history_result = requests.get(request_url, params=params)
        return txs_history_result.text

    def orders_history(self, offset: int = 0, limit: int = 50):

        data = {
            "request": self.ORDERS_HISTORY_ENDPOINT,
            "nonce": str(time() * 1000),
        }

        payload = base64.b64encode(ujson.dumps(data, escape_forward_slashes=False).encode('utf-8'))
        signature = hmac.new(self.pr_key.encode("utf-8"), payload, hashlib.sha512).hexdigest()
        headers = {
            "Content-type": "application/json",
            "X-TXC-APIKEY": self.pub_key,
            "X-TXC-PAYLOAD": payload,
            "X-TXC-SIGNATURE": signature
        }
        request_url = self.BASE_URL + self.ORDERS_HISTORY_ENDPOINT
        params = {
            'offset': offset,
            'limit': limit
        }
        orders_history_result = requests.post(request_url, headers=headers, params=params, data=codecs.escape_encode(ujson.dumps(data, escape_forward_slashes=False).encode("utf8"))[0])
        return orders_history_result.text

    def place_order(self, tickers: List, side: str = 'sell', amount: str = '0.1', price: str = '0.1'):

        data = {
            "request": self.PLACE_ORDER_ENDPOINT,
            "nonce": str(time() * 1000),
        }

        payload = base64.b64encode(ujson.dumps(data, escape_forward_slashes=False).encode('utf-8'))
        signature = hmac.new(self.pr_key.encode("utf-8"), payload, hashlib.sha512).hexdigest()
        headers = {
            "Content-type": "application/json",
            "X-TXC-APIKEY": self.pub_key,
            "X-TXC-PAYLOAD": payload,
            "X-TXC-SIGNATURE": signature
        }

        tickers = [ticker.upper() for ticker in tickers]
        currency_pair_code = tickers[0] + "_" + tickers[1]

        params = {
            "market": currency_pair_code,
            "side": side,
            "amount": amount,
            "price": price
        }
        request_url = self.BASE_URL + self.PLACE_ORDER_ENDPOINT
        place_order_result = requests.request('POST', request_url, headers=headers, params=params, data=codecs.escape_encode(ujson.dumps(data, escape_forward_slashes=False).encode("utf8"))[0])
        return place_order_result.text

    def cancel_order(self, tickers: List, OrderId: int):
        data = {
            "request": self.CANCEL_ORDER_ENDPOINT,
            "nonce": str(time() * 1000),
        }

        payload = base64.b64encode(ujson.dumps(data, escape_forward_slashes=False).encode('utf-8'))
        signature = hmac.new(self.pr_key.encode("utf-8"), payload, hashlib.sha512).hexdigest()
        headers = {
            "Content-type": "application/json",
            "X-TXC-APIKEY": self.pub_key,
            "X-TXC-PAYLOAD": payload,
            "X-TXC-SIGNATURE": signature
        }

        tickers = [ticker.upper() for ticker in tickers]
        currency_pair_code = tickers[0] + "_" + tickers[1]

        params = {
            "market": currency_pair_code,
            "OrderId": OrderId
        }
        request_url = self.BASE_URL + self.PLACE_ORDER_ENDPOINT
        cancel_order_result = requests.request('POST', request_url, headers=headers, params=params, data=
        codecs.escape_encode(ujson.dumps(data, escape_forward_slashes=False).encode("utf8"))[0])

        return cancel_order_result


if __name__ == '__main__':
    r = Coinsbit_API('be6e4a9feb06fa5f60dd27dffb6878c6', 'a58369c8d86ca9d6b96f192a0016b9bc')
    print('current_order_book', r.current_order_book(['BNB', 'USDT']))
    print('current_balances', r.current_balances("BNB"))
    print('orders in market', r.orders_in_market(['BNB', 'USDT']))
    print('Please enter OrderID')
    print('current_transactions', r.current_transactions(input()))
    print('orders_history', r.orders_history())
    print('txs_history', r.txs_history(['BNB', 'USDT'], 1))


