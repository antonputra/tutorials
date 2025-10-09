import requests
import hmac
import hashlib
from urllib.parse import urlencode, quote
import config

# ServerTime、Signature
class TOOL(object):

    @staticmethod
    def _get_server_time():
        return requests.request('get', 'https://api.mexc.com/api/v3/time').json()['serverTime']

    def _sign_v3(self, req_time, sign_params=None):
        if sign_params:
            sign_params = urlencode(sign_params, quote_via=quote)
            to_sign = "{}&timestamp={}".format(sign_params, req_time)
        else:
            to_sign = "timestamp={}".format(req_time)
        sign = hmac.new(self.mexc_secret.encode('utf-8'), to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        return sign

    def public_request(self, method, url, params=None):
        url = '{}{}'.format(self.hosts, url)
        return requests.request(method, url, params=params)

    def sign_request(self, method, url, params=None):
        url = '{}{}'.format(self.hosts, url)
        req_time = self._get_server_time()
        if params:
            params['signature'] = self._sign_v3(req_time=req_time, sign_params=params)
        else:
            params = {'signature': self._sign_v3(req_time=req_time)}
        params['timestamp'] = req_time
        headers = {
            'x-mexc-apikey': self.mexc_key,
            'Content-Type': 'application/json',
        }
        return requests.request(method, url, params=params, headers=headers)


# Market Data
class mexc_market(TOOL):

    def __init__(self):
        self.api = '/api/v3'
        self.hosts = config.mexc_host
        self.method = 'GET'

    def get_ping(self):
        """Ping
        Test connectivity to the Rest API.

        GET /api/v3/ping

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#test-connectivity
        """
        url = '{}{}'.format(self.api, '/ping')
        response = self.public_request(self.method, url)
        return response.json()

    def get_timestamp(self):
        """Check Server Time

        GET /api/v3/time

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#check-server-time
        """
        url = '{}{}'.format(self.api, '/time')
        response = self.public_request(self.method, url)
        return response.json()

    def get_defaultSymbols(self):
        """Get Default Symbols

        GET /api/v3/defaultSymbols

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#api-default-symbol
        """
        url = '{}{}'.format(self.api, '/defaultSymbols')
        response = self.public_request(self.method, url)
        return response.json()

    def get_exchangeInfo(self, params=None):
        """Exchange Information
        Current exchange trading rules and symbol information

        GET /api/v3/exchangeInfo

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#exchange-information

        params:
            symbol (str, optional): the trading pair
            symbols (str, optional): the trading pairs (symbols="MXUSDT,BTCUSDT")
        """
        url = '{}{}'.format(self.api, '/exchangeInfo')
        response = self.public_request(self.method, url, params=params)
        return response.json()

    def get_depth(self, params):
        """Order Book

        GET /api/v3/depth

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#order-book

        params:
            symbol (str): the trading pair
            limit (int, optional): limit the results. Default 100; max 5000
        """
        url = '{}{}'.format(self.api, '/depth')
        response = self.public_request(self.method, url, params=params)
        return response.json()

    def get_deals(self, params):
        """Recent Trades List

        GET /api/v3/trades

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#recent-trades-list

        params:
            symbol (str): the trading pair
            limit (int, optional): limit the results. Default 500; max 1000
        """
        url = '{}{}'.format(self.api, '/trades')
        response = self.public_request(self.method, url, params=params)
        return response.json()

    def get_aggtrades(self, params):
        """Compressed/Aggregate Trades List
        Get compressed/aggregate trades. Trades that fill at the time, from the same order, with the same price will
        have the quantity aggregated.

        GET /api/v3/aggTrades

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#compressed-aggregate-trades-list

        params:
            symbol (str): the trading pair
            startTime (int, optional): Timestamp in ms to get aggregate trades from INCLUSIVE.
            endTime (int, optional): Timestamp in ms to get aggregate trades from INCLUSIVE.
            limit (int, optional): limit the results. Default 500; max 1000
        """
        url = '{}{}'.format(self.api, '/aggTrades')
        response = self.public_request(self.method, url, params=params)
        return response.json()

    def get_kline(self, params):
        """Kline/Candlestick Data
        Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time.

        GET /api/v3/klines

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#kline-candlestick-data

        params:
            symbol (str): the trading pair
            interval (str): the interval of kline, e.g 1m, 5m, 60m, 4h
            limit (int, optional): limit the results. Default 500; max 1000.
            startTime (int, optional): Timestamp in ms to get aggregate trades from INCLUSIVE.
            endTime (int, optional): Timestamp in ms to get aggregate trades until INCLUSIVE.
        """
        url = '{}{}'.format(self.api, '/klines')
        response = self.public_request(self.method, url, params=params)
        return response.json()

    def get_avgprice(self, params):
        """Current Average Price

        GET /api/v3/avgPrice

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#current-average-price

        params:
            symbol (str): the trading pair
        """
        url = '{}{}'.format(self.api, '/avgPrice')
        response = self.public_request(self.method, url, params=params)
        return response.json()

    def get_24hr_ticker(self, params=None):
        """24hr Ticker Price Change Statistics

        GET /api/v3/ticker/24hr

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#24hr-ticker-price-change-statistics

        params:
            symbol (str, optional): the trading pair
        """
        url = '{}{}'.format(self.api, '/ticker/24hr')
        response = self.public_request(self.method, url, params=params)
        return response.json()

    def get_price(self, params=None):
        """Symbol Price Ticker

        GET /api/v3/ticker/price

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#symbol-price-ticker

        params:
            symbol (str, optional): the trading pair
        """
        url = '{}{}'.format(self.api, '/ticker/price')
        response = self.public_request(self.method, url, params=params)
        return response.json()

    def get_bookticker(self, params=None):
        """Symbol Order Book Ticker
        Best price/qty on the order book for a symbol or symbols

        GET /api/v3/ticker/bookTicker

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#symbol-order-book-ticker

        params:
            symbol (str, optional): the trading pair
        """
        url = '{}{}'.format(self.api, '/ticker/bookTicker')
        response = self.public_request(self.method, url, params=params)
        return response.json()

    def get_ETF_info(self, params=None):
        """ETF Information
        Get information on ETFs, such as symbol, netValue and fund fee.

        GET api/v3/etf/info

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#etf
        """
        url = '{}{}'.format(self.api, '/etf/info')
        response = self.public_request(self.method, url, params=params)
        return response.json()


# Spot Trade
class mexc_trade(TOOL):

    def __init__(self):
        self.api = '/api/v3'
        self.hosts = config.mexc_host
        self.mexc_key = config.api_key
        self.mexc_secret = config.secret_key

    def get_kyc_status(self):
        """Query KYC status

        GET /api/v3/kyc/status

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-kyc-status
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/kyc/status')
        response = self.sign_request(method, url)
        return response.json()

    def get_selfSymbols(self):
        """User API default symbol

        GET /api/v3/selfSymbols

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#user-api-default-symbol
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/selfSymbols')
        response = self.sign_request(method, url)
        return response.json()

    def post_order_test(self, params):
        """Test New Order
        Creates and validates a new order but does not send it into the matching engine.

        POST /api/v3/order/test

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#test-new-order
        """
        method = 'POST'
        url = '{}{}'.format(self.api, '/order/test')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def post_order(self, params):
        """New Order

        Post New Order

        POST /api/v3/order

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#new-order
        """
        method = 'POST'
        url = '{}{}'.format(self.api, '/order')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def post_batchorders(self, params):
        """Post Batch Orders
        Supports 20 orders with a same symbol in a batch

        POST /api/v3/batchOrders

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#batch-orders
        """
        method = 'POST'
        url = '{}{}'.format(self.api, '/batchOrders')
        params = {"batchOrders": str(params)}
        response = self.sign_request(method, url, params=params)
        print(response.url)
        return response.json()

    def delete_order(self, params):
        """Cancel Order
        Cancel an active order.

        DELETE /api/v3/order

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#cancel-order
        Either 'origClientOrderId' or 'orderId' must be sent.
        """
        method = 'DELETE'
        url = '{}{}'.format(self.api, '/order')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def delete_openorders(self, params):
        """Cancel all order for a single symbol
        Cancel all pending orders for a single symbol, including OCO pending orders.

        DELETE /api/v3/openOrders

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#cancel-all-open-orders-on-a-symbol
        """
        method = 'DELETE'
        url = '{}{}'.format(self.api, '/openOrders')
        response = self.sign_request(method, url, params=params)
        print(response.url)
        return response.json()

    def get_order(self, params):
        """Query Order
        Check an order's status

        GET /api/v3/order

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-order
        Either 'origClientOrderId' or 'orderId' must be sent
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/order')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_openorders(self, params):
        """Current Open Orders
        Get all open orders on a symbol. Careful when accessing this with no symbol.

        GET /api/v3/openOrders

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#current-open-orders
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/openOrders')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_allorders(self, params):
        """All Orders
        Get all account orders including active, cancelled or completed orders(the query period is the latest 24 hours
        by default).You can query a maximum of the latest 7 days.

        GET /api/v3/allOrders

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#all-orders
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/allOrders')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_trades(self, params):
        """Account Trade List
        Get trades for a specific account and symbol, only the transaction records in the past 1 month cna be queried.
        If you want to view more transaction records, please use the export function on the web side, which supports
        exporting transaction records of the past 3 years at most.

        GET /api/v3/myTrades

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#account-trade-list
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/myTrades')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def post_mxDeDuct(self, params):
        """Enable MX DeDuct
        Enable or disable MX deduct for spot commission fee

        POST api/v3/mxDeduct/enable

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#enable-mx-deduct
        """
        method = 'POST'
        url = '{}{}'.format(self.api, '/mxDeduct/enable')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_mxDeDuct(self):
        """Query MX Deduct Status

        GET api/v3/mxDeduct/enable

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-mx-deduct-status
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/mxDeduct/enable')
        response = self.sign_request(method, url)
        return response.json()

    def get_symbol_commission(self, params):
        """Query Symbol Commission

        GET api/v3/tradeFee

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-symbol-commission
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/tradeFee')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_account_info(self):
        """Account Information
        Get current account information

        GET /api/v3/account

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#account-information
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/account')
        response = self.sign_request(method, url)
        return response.json()


# Wallet
class mexc_wallet(TOOL):

    def __init__(self):
        self.api = '/api/v3/capital'
        self.hosts = config.mexc_host
        self.mexc_key = config.api_key
        self.mexc_secret = config.secret_key

    def get_coinlist(self):
        """Query the currency information
        Query currency details and the smart contract address.

        GET /api/v3/capital/config/getall

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#wallet-endpoints
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/config/getall')
        response = self.sign_request(method, url)
        return response.json()

    def post_withdraw(self, params):
        """Withdraw

        POST /api/v3/capital/withdraw

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#withdraw-new
        Can get netWork via endpoints Get /api/v3/capital/config/getall's response params networkList.
        """
        method = 'POST'
        url = '{}{}'.format(self.api, '/withdraw')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def cancel_withdraw(self, params):
        """Cancel Withdraw

        DELETE /api/v3/capital/withdraw

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#cancel-withdraw
        """
        method = 'DELETE'
        url = '{}{}'.format(self.api, '/withdraw')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_deposit_list(self, params):
        """Deposit History(supporting network)

        GET /api/v3/capital/deposit/hisrec

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#deposit-history-supporting-network
        1. default return the records of the last 7 days.
        2. Ensure that the default timestamp of 'startTime' and 'endTime' does not exceed 7 days.
        3. can query 90 days data at most.
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/deposit/hisrec')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_withdraw_list(self, params):
        """Withdraw History(supporting network)

        GET /api/v3/capital/withdraw/history

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#withdraw-history-supporting-network
        1. default return the records of the last 7 days.
        2. Ensure that the default timestamp of 'startTime' and 'endTime' does not exceed 7 days.
        3. can query 90 days data at most.
        5. Supported multiple net work coins's withdraw history may not return the 'network' field.
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/withdraw/history')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def post_deposit_address(self, params):
        """Generate deposit address(supporting network)

        POST /api/v3/capital/deposit/address

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#generate-deposit-address-supporting-network
        """
        method = 'POST'
        url = '{}{}'.format(self.api, '/deposit/address')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_deposit_address(self, params):
        """Deposit Address(supporting network)

        GET /api/v3/capital/deposit/address

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#deposit-address-supporting-network
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/deposit/address')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_withdraw_address(self, params):
        """Withdraw Address(supporting network)

        GET /api/v3/capital/withdraw/address

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#withdraw-address-supporting-network
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/withdraw/address')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def post_transfer(self, params):
        """User Universal Transfer

        POST /api/v3/capital/transfer

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#user-universal-transfer
        """
        method = 'POST'
        url = '{}{}'.format(self.api, '/transfer')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_transfer_list(self, params):
        """Query User Universal Transfer History

        GET /api/v3/capital/transfer

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-user-universal-transfer-history
        1. Only can query the data for the last six months.
        2. If 'startTime' and 'endTime' are not send, will return the last seven days data by default.
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/transfer')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_transfer_list_byId(self, params):
        """Query User Universal Transfer History (by tranId)

        GET /api/v3/capital/transfer/tranId

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-user-universal-transfer-history-by-tranid
        Only can query the data for the last six months
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/transfer/tranId')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_smallAssets_list(self):
        """Get Assets that Can be Converted Into MX

        GET /api/v3/capital/convert/list

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-assets-that-can-be-converted-into-mx
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/convert/list')
        response = self.sign_request(method, url)
        return response.json()

    def post_smallAssets_convert(self, params):
        """Dust Transfer

        POST /api/v3/capital/convert

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#dust-transfer
        """
        method = 'POST'
        url = '{}{}'.format(self.api, '/convert')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_smallAssets_converted_history(self, params=None):
        """DustLog

        GET /api/v3/capital/convert

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#dustlog
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/convert')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def post_transfer_internal(self, params):
        """Internal Transfer

        POST /api/v3/capital/transfer/internal

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#internal-transfer
        """
        method = 'POST'
        url = '{}{}'.format(self.api, '/transfer/internal')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_transfer_internal_list(self, params=None):
        """Query Internal Transfer History

        GET /api/v3/capital/transfer/internal

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-internal-transfer-history
        If startTime and endTime are not send, will default to returning data from the last 7 days.
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/transfer/internal')
        response = self.sign_request(method, url, params=params)
        return response.json()


# Sub-Account
class mexc_subaccount(TOOL):

    def __init__(self):
        self.api = '/api/v3'
        self.hosts = config.mexc_host
        self.mexc_key = config.api_key
        self.mexc_secret = config.secret_key

    def post_virtualSubAccount(self, params):
        """Create a Sub-account(For Master Account)
        Create a sub-account from the master account.

        POST / api/v3/sub-account/virtualSubAccount

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#create-a-sub-account-for-master-account
        """
        method = 'POST'
        url = '{}{}'.format(self.api, '/sub-account/virtualSubAccount')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_SubAccountList(self, params=None):
        """Query Sub-account List(For Master Account)
        Get details of the sub-account list

        GET / api/v3/sub-account/list

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-sub-account-list-for-master-account
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/sub-account/list')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def post_subaccount_ApiKey(self, params):
        """Create an APIKEY for a sub-account(For Master Account)

        POST /api/v3/sub-account/apiKey

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#create-an-apikey-for-a-sub-account-for-master-account
        """
        method = 'POST'
        url = '{}{}'.format(self.api, '/sub-account/apiKey')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_subaccount_ApiKey(self, params):
        """Query the APIKEY of a sub-account(For Master Account)
        Applies to master accounts only

        GET/api/v3/sub-account/apiKey

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-the-apikey-of-a-sub-account-for-master-account
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/sub-account/apiKey')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def delete_subaccount_ApiKey(self, params):
        """Delete the APILEY of a sub-account(For Master Account)

        DELETE /api/v3/sub-account/apiKey

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#delete-the-apikey-of-a-sub-account-for-master-account
        """
        method = 'DELETE'
        url = '{}{}'.format(self.api, '/sub-account/apiKey')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def post_universalTransfer(self, params):
        """Universal Transfer(For Master Account)

        POST /api/v3/capital/sub-account/universalTransfer

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#universal-transfer-for-master-account
        """
        method = 'POST'
        url = '{}{}'.format(self.api, '/capital/sub-account/universalTransfer')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_universalTransfer(self, params):
        """Query Universal Transfer History(For Master Account)

        GET /api/v3/capital/sub-account/universalTransfer

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-universal-transfer-history-for-master-account
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/capital/sub-account/universalTransfer')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_subaccount_asset(self, params):
        """Query Sub-account Asset

        GET /api/v3/sub-account/asset

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-sub-account-asset
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/sub-account/asset')
        response = self.sign_request(method, url, params=params)
        return response.json()


# Rebate
class mexc_rebate(TOOL):

    def __init__(self):
        self.api = '/api/v3/rebate'
        self.hosts = config.mexc_host
        self.mexc_key = config.api_key
        self.mexc_secret = config.secret_key

    def get_taxQuery(self, params=None):
        """Get Rebate History Records

        GET /api/v3/rebate/taxQuery

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-rebate-history-records
        If 'startTime' and 'endTime' are not send, the recent 1 year's data will be returned.
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/taxQuery')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_rebate_detail(self, params=None):
        """Get Rebate Records Detail

        GET /api/v3/rebate/detail

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-rebate-records-detail
        If 'startTime' and 'endTime' are not send, the recent 1 year's data will be returned.
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/detail')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_kickback_detail(self, params=None):
        """Get Self Rebate Records Detail

        GET /api/v3/rebate/detail/kickback

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-self-rebate-records-detail
        If 'startTime' and 'endTime' are not send, the recent 1 year's data will be returned.
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/detail/kickback')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_refercode(self, params=None):
        """Query ReferCode

        GET /api/v3/rebate/referCode

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-refercode
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/referCode')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_affiliate_commission(self, params=None):
        """Get Affiliate Commission Record(affiliate only)

        GET /api/v3/rebate/affiliate/commission

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-affiliate-commission-record-affiliate-only
        If 'startTime' and 'endTime' are not send, the recent 1 year's data will be returned.
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/affiliate/commission')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_affiliate_withdraw(self, params=None):
        """Get Affiliate Withdraw Record(affiliate only)

        GET /api/v3/rebate/affiliate/withdraw

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-affiliate-withdraw-record-affiliate-only
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/affiliate/withdraw')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_affiliate_commission_detail(self, params=None):
        """Get Affiliate Commission Detail Record(affiliate only)

        GET /api/v3/rebate/affiliate/commission/detail

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-affiliate-commission-detail-record-affiliate-only
        If startTime and endTime are not sent, the data from T-7 to T is returned. If type is not sent, the data of
        all types is returned,maximum 30 days data can be queried at one time.
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/affiliate/commission/detail')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_affiliate_campaign(self, params=None):
        """Get Affiliate Campaign Data(affiliate only)

        GET /api/v3/rebate/affiliate/campaign

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-affiliate-campaign-data-affiliate-only
        If startTime and endTime are not sent, the data from T-7 to T is returned.
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/affiliate/referral')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_affiliate_referral(self, params=None):
        """Get Affiliate Referral Data(affiliate only)

        GET /api/v3/rebate/affiliate/referral

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-affiliate-referral-data-affiliate-only
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/affiliate/referral')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def get_affiliate_subaffiliates(self, params=None):
        """Get Subaffiliates Data(affiliate only)

        GET /api/v3/rebate/affiliate/subaffiliates

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-subaffiliates-data-affiliate-only
        If startTime and endTime are not sent, the data from T-7 to T is returned.
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/affiliate/subaffiliates')
        response = self.sign_request(method, url, params=params)
        return response.json()


# WebSocket ListenKey
class mexc_listenkey(TOOL):

    def __init__(self):
        self.api = '/api/v3'
        self.hosts = config.mexc_host
        self.mexc_key = config.api_key
        self.mexc_secret = config.secret_key

    def post_listenKey(self):
        """Create a ListenKey
        Start a new user data stream. The stream will close after 60 minutes unless a keepalive is sent.

        POST /api/v3/userDataStream

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#listen-key
        """
        method = 'POST'
        url = '{}{}'.format(self.api, '/userDataStream')
        response = self.sign_request(method, url)
        return response.json()

    def get_listenKey(self):
        """ Query all ListenKey
        Get all valid ListenKey.

        GET /api/v3/userDataStream

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#listen-key
        """
        method = 'GET'
        url = '{}{}'.format(self.api, '/userDataStream')
        response = self.sign_request(method, url)
        return response.json()

    def put_listenKey(self, params):
        """Keep-alive a ListenKey
        Keepalive a user data stream tp prevent a time out. User data streams will close after 60 minutes. It's
        recommended to send a ping about every 30 minutes.

        PUT /api/v3/userDataStream

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#listen-key
        """
        method = 'PUT'
        url = '{}{}'.format(self.api, '/userDataStream')
        response = self.sign_request(method, url, params=params)
        return response.json()

    def delete_listenKey(self, params):
        """delete ListenKey
        Close a ListenKey

        DELETE /api/v3/userDataStream

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#listen-key
        """
        method = 'DELETE'
        url = '{}{}'.format(self.api, '/userDataStream')
        response = self.sign_request(method, url, params=params)
        return response.json()
