import hmac
import hashlib
import requests
import json

from typing import Tuple, List, Dict

class Config():

    C3_PR_KEY = ""
    C3_PUB_KEY = ""



class C3_API(object):
    def __init__(self, prKey: str, pubKey: str) -> None:

        self.prKey = prKey
        self.pubKey = pubKey

        # Base URL
        self.BASE_URL = "https://api.c3.exchange"

        # Account Endpoints
        self.CURRENT_BALANCES_ENDPOINT = "/api/wallets/balances" # [GET]
        self.ORDERS_IN_MARKET_ENDPOINT = "/api/user/orders" # [GET]
        self.TXS_HISTORY_ENDPOINT = "/api/user/deals" # [GET]
        self.ORDERS_HISTORY_ENDPOINT = "/api/user/orders" # [GET]

        # Current Market Endpoints
        self.CURRENT_ORDER_BOOK_ENDPOINT = "/api/orderbook" # [GET]
        self.CURRENT_TRANSACTIONS_ENDPOINT = "/api/deals" # [GET]
        self.LAST_PRICE_ENDPOINT = "/api/tickers" # [GET]

        # Trade Endpoints
        self.PLACE_ORDER_ENDPOINT = "/api/orders"   # [POST] + Header: API-pubKey and API-sig;
                                                    #        + json payload, ex.:
                                                    #        {
                                                    #         "side": "buy",
                                                    #         "currencyPairCode": "BTC_USDT",
                                                    #         "amount": 0.001,
                                                    #         "price": 45000
                                                    #        }
        self.CANCEL_ORDER_ENDPOINT = "/api/orders/" # [DELETE] + /{orderId}


    # ===== ACCOUNT ENDPOINTS =====
    def getCurrentBalances(self, tickers: list) -> List[dict]:

        """
        Gets currency codes, prepares cryptography signiture and exchange request
        and returns account balances.
        """

        # Generate msg to sign
        requestUrl = self.BASE_URL+self.CURRENT_BALANCES_ENDPOINT
        msg = self.pubKey+requestUrl
        msg = msg.encode("utf-8")
        pubKey = self.pubKey.encode("utf-8")
        prKey = self.prKey.encode("utf-8")

        # Sign message
        signature = hmac.new(prKey, msg, hashlib.sha256).hexdigest()

        # Create and send request
        headers = {
                    "API-PublicKey": pubKey,
                    "API-Signature": signature,
                }

        balances = json.loads(requests.get(requestUrl, headers=headers).content)

        # Make tickers upper case just in case
        tickers = [ticker.upper() for ticker in tickers]
        # Get target balances
        returnBalances = [balance for balance in balances['balances'] if balance['currencyCode'] in tickers]

        return returnBalances


    def getCurrentOrders(self, tickers: list) -> List[dict]:

        """
        Gets currencies codes to build currencyPairCode, prepares cryptography signiture and exchange request
        and returns active market orders.
        """
        tickers = [ticker.upper() for ticker in tickers]
        currencyPairCode = tickers[0]+"_"+tickers[1]

        # Generate msg to sign
        requestUrl = self.BASE_URL+self.ORDERS_IN_MARKET_ENDPOINT
        requestBody = f"?currencyPairCode={currencyPairCode}&status=active"

        msg = self.pubKey+requestUrl+requestBody
        msg = msg.encode("utf-8")
        pubKey = self.pubKey.encode("utf-8")
        prKey = self.prKey.encode("utf-8")

        # Sign message
        signature = hmac.new(prKey, msg, hashlib.sha256).hexdigest()

        # Create and send request
        headers = {
            "API-PublicKey": pubKey,
            "API-Signature": signature,
        }

        requestMsg = requestUrl+requestBody
        currentOrders = json.loads(requests.get(requestMsg, headers=headers).content)

        return currentOrders


    def getTxsHistory(self, tickers: list, returnSize: int = 50) -> List[dict]:

        """
        Gets currencies codes to build currencyPairCode, prepares cryptography signiture and exchange request
        and returns 50 last txs.

        Attention! Request could be processing around 3-4 seconds on server side!!!
        """

        tickers = [ticker.upper() for ticker in tickers]
        currencyPairCode = tickers[0]+"_"+tickers[1]

        # Generate msg to sign
        requestUrl = self.BASE_URL+self.TXS_HISTORY_ENDPOINT
        requestBody = f"?currencyPairCode={currencyPairCode}&pageSize={returnSize}"

        msg = self.pubKey+requestUrl+requestBody
        msg = msg.encode("utf-8")
        pubKey = self.pubKey.encode("utf-8")
        prKey = self.prKey.encode("utf-8")

        # Sign message
        signature = hmac.new(prKey, msg, hashlib.sha256).hexdigest()

        # Create and send request
        headers = {
            "API-PublicKey": pubKey,
            "API-Signature": signature,
        }

        requestMsg = requestUrl+requestBody
        txsHistory = json.loads(requests.get(requestMsg, headers=headers).content)

        return txsHistory


    # ===== CURRENT MARKET ENDPOINTS =====
    def getCurrentOrderbook(self, tickers: list) -> List[dict]:

        """
        Gets currencies codes to build currencyPairCode, prepares exchange request
        and returns 40 current asks and bids.
        """

        tickers = [ticker.upper() for ticker in tickers]
        currencyPairCode = tickers[0]+"_"+tickers[1]

        requestUrl = self.BASE_URL+self.CURRENT_ORDER_BOOK_ENDPOINT
        requestBody = f"?currencyPairCode={currencyPairCode}"
        requestMsg = requestUrl+requestBody

        orderBook = json.loads(requests.get(requestMsg).content)

        return orderBook


    def getCurrentTxs(self, tickers: list, returnSize: int = 50) -> List[dict]:

        """
        Gets currencies codes to build currencyPairCode, prepares exchange request
        and returns 50 current pair trades.

        Attention! Request could be processing around 4-5 seconds on server side!!!
        """

        tickers = [ticker.upper() for ticker in tickers]
        currencyPairCode = tickers[0]+"_"+tickers[1]

        requestUrl = self.BASE_URL+self.CURRENT_TRANSACTIONS_ENDPOINT
        requestBody = f"?currencyPairCode={currencyPairCode}&pageSize={returnSize}"
        requestMsg = requestUrl+requestBody

        currentTxs = json.loads(requests.get(requestMsg).content)

        return currentTxs


    def getLastPrice(self, tickers: list) -> float:

        """
        Gets currencies codes to build currencyPairCode, prepares exchange request
        and returns last market price.

        NOTE! Original API response contains best ask and best bid.
        """

        tickers = [ticker.upper() for ticker in tickers]
        currencyPairCode = tickers[0]+"_"+tickers[1]

        requestUrl = self.BASE_URL+self.LAST_PRICE_ENDPOINT
        requestBody = f"?currencyPairCode={currencyPairCode}"
        requestMsg = requestUrl+requestBody

        lastPrice = json.loads(requests.get(requestMsg).content)['price']

        return lastPrice


    # ===== TRADE ENDPOINTS =====
    def placeOrder(self, tickers: list, orderData: dict):
        """
        Creates and sends limit order to the exchange in format:
        {
          "side": "buy",
          "currencyPairCode": "BTC_USDT",
          "amount": 0.001,
          "price": 45000
        }

        """
        tickers = [ticker.upper() for ticker in tickers]
        currencyPairCode = tickers[0]+"_"+tickers[1]

        # Generate msg to sign
        requestUrl = self.BASE_URL+self.PLACE_ORDER_ENDPOINT
        requestBody = {
            "isBid": False if orderData["direction"].lower() == 'sell' else True,
            "side": orderData["direction"].lower(),   #было закомменчено
            "currencyPairCode": currencyPairCode,
            "amount": float(orderData["volume"]),
            "price": int(orderData["price"]),  #здесь был float
        }

        msg = self.pubKey+requestUrl+str(requestBody)
        msg = msg.replace(" ", "")
        print(msg)
        msg = msg.encode("utf-8")
        pubKey = self.pubKey.encode("utf-8")
        prKey = self.prKey.encode("utf-8")

        # Sign message
        signature = hmac.new(prKey, msg, hashlib.sha256).hexdigest()
        print(signature)

        # Create and send request
        headers = {
            "API-PublicKey": pubKey,
            "API-Signature": signature,
        }

        # requestMsg = requestUrl+str(requestBody).replace(" ", "")
        # print(requestMsg)
        orderPlaceResult = requests.post(requestUrl, headers=headers, data=json.dumps(requestBody).replace(" ", "")).content

        return orderPlaceResult


    def cancelOrder(self, orderId: str):
        # Generate msg to sign
        
        requestUrl = self.BASE_URL+self.PLACE_ORDER_ENDPOINT
        
        msg = self.pubKey + requestUrl + str(requestBody)
        msg = msg.replace(" ", "")
        print(msg)
        msg = msg.encode("utf-8")
        pubKey = self.pubKey.encode("utf-8")
        prKey = self.prKey.encode("utf-8")

        # Sign message
        signature = hmac.new(prKey, msg, hashlib.sha256).hexdigest()
        print(signature)

        # Create and send request
        headers = {
            "API-PublicKey": pubKey,
            "API-Signature": signature,
        }
        
        requestMsg = requestUrl + '/' + orderId
        result = requests.delete(requestMsg, headers=headers)

        return result

res = C3_API('JnNw3Wnx5QIBfjHSksYVFXEsbulcBO2uOJQln3woDGsizvervidJNk3gXE2rqzEUyNgCzg', 'QWn55oJdZofjXUv4JKN9LKarNkahzLqq84Nt_g')
print(res.getCurrentTxs(['DEL', 'USDT']))
print(res.getCurrentOrders(['DEL', 'USDT']))
print(res.getTxsHistory(['BNB', 'USDT']))

