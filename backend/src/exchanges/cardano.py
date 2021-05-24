from aiohttp.client import request
import graphene
import aiohttp
import json

from mongoengine.queryset.transform import query
from .meta_exchange import MetaExchange, Ticker, Balance, Order, make_coins
import time
import hashlib
import hmac
import random
from operator import itemgetter

BASE_URL = 'https://cardano-mainnet.blockfrost.io/api/v0'
API_KEY = ''
API_SECRET = ''

async def gen_request(uri, method, api_key, body=None):

    header = {"project_id": api_key}

    return await fetch(uri, method, headers=header)

async def fetch(url, request_type, body=None, headers=None):
    async with aiohttp.ClientSession() as session:
        
        params = {}
        params['url']           = url
        if body:
            params['json']      = body
        if headers:
            params['headers']   = headers

        async with getattr(session, request_type)(**params) as resp:
            print(resp.status)
            resp = await resp.text()
            return json.loads(resp)

class Cardano(graphene.ObjectType):
    class Meta:
        interfaces = (MetaExchange,)

    async def resolve_balance(self, info, api_key="", api_secret=""):
        if api_key == "":
            api_key = info.context['user']['exchanges']['cardano']['api_key']
        if api_secret == "":
            api_secret = info.context['user']['exchanges']['cardano']['api_secret']
        
        tic = time.perf_counter()

        response = await gen_request(BASE_URL + f"/accounts/{api_secret}", 'get', api_key=api_key)

        if 'code' in response and response['code'] != 200:
            raise Exception(response['msg'])
        
        balances = [{"name": 'Cardano', "symbol": 'ADA', "balance": int(response['controlled_amount']) / 1000000}]
        coins = await make_coins(info.context, balances, 'symbol', 'balance', 'balance')
        
        toc = time.perf_counter()
        print(f'cardano, balance: {round(toc-tic, 2)}s')
        return coins

    # async def resolve_orders(self, info, order_type="", api_key="", api_secret=""):
    #     #TODO: Fix api keys here
    #     response = await gen_request(BASE_URL + f'/orders/{order_type}', 'get', api_secret, api_key)
    #     orders = [
    #         Order(
    #             id          = order['id'],
    #             market      = order['marketSymbol'],
    #             direction   = order['direction'],
    #             order_type  = order['type'],
    #             quantity    = order['quantity'],
    #             limit       = order['limit'] if 'limit' in order else '',
    #             timeInForce = order['timeInForce'],
    #             fillQuantity= order['fillQuantity'],
    #             commission  = order['commission'],
    #             proceeds    = order['proceeds'],
    #             created     = order['createdAt'],
    #             updated     = order['updatedAt'],
    #             closed      = order['closedAt']
    #         ) 
    #         for order in response
    #         ]
    #     return orders

    async def resolve_tickers(self, info):
        response = await fetch(f'https://api.coingecko.com/api/v3/exchanges/bittrex/tickers', request_type='get')
        tickers = [Ticker(name=ticker['base'], usd=ticker['converted_last']['usd']) for ticker in response['tickers']]
        return tickers