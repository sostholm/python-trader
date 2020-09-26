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

BASE_URL = 'https://api.binance.com/api/v3'
API_KEY = ''
API_SECRET = ''

def _order_params(data):
    """Convert params to list with signature as last element

    :param data:
    :return:

    """
    has_signature = False
    params = []
    for key, value in data.items():
        if key == 'signature':
            has_signature = True
        else:
            params.append((key, value))
    # sort parameters by key
    params.sort(key=itemgetter(0))
    if has_signature:
        params.append(('signature', data['signature']))
    return params

def sign(params, api_secret):
    ordered_data = _order_params(params)
    query_string = '&'.join(["{}={}".format(d[0], d[1]) for d in ordered_data])
    m = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
    return m.hexdigest()

async def gen_request(uri, method, api_secret, api_key, body=None):
    params = dict(
        timestamp = int(time.time() * 1000),
        recvWindow = 20000,
    )

    params['signature'] = sign(params, api_secret)
    ordered_data = _order_params(params)
    query_string = '&'.join(["{}={}".format(d[0], d[1]) for d in ordered_data])

    header = {"X-MBX-APIKEY": api_key}

    return await fetch(uri + '?' + query_string, method, headers=header)

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

class Binance(graphene.ObjectType):
    class Meta:
        interfaces = (MetaExchange,)

    async def resolve_balance(self, info, api_key="", api_secret=""):
        if api_key == "":
            api_key = info.context['user'].exchanges['binance']['api_key']
        if api_secret == "":
            api_secret = info.context['user'].exchanges['binance']['api_secret']
        
        tic = time.perf_counter()



        response = await gen_request(BASE_URL + "/account", 'get', api_secret=api_secret, api_key=api_key)

        if 'code' in response and response['code'] != 200:
            raise Exception(response['msg'])
        coins = make_coins(info.context, response['balances'], 'asset', 'free_locked', 'free')
        
        toc = time.perf_counter()
        print(f'binance, balance: {round(toc-tic, 2)}s')
        return coins

    async def resolve_orders(self, info, order_type="", api_key="", api_secret=""):
        #TODO: Fix api keys here
        response = await gen_request(BASE_URL + f'/orders/{order_type}', 'get', api_secret, api_key)
        orders = [
            Order(
                id          = order['id'],
                market      = order['marketSymbol'],
                direction   = order['direction'],
                order_type  = order['type'],
                quantity    = order['quantity'],
                limit       = order['limit'] if 'limit' in order else '',
                timeInForce = order['timeInForce'],
                fillQuantity= order['fillQuantity'],
                commission  = order['commission'],
                proceeds    = order['proceeds'],
                created     = order['createdAt'],
                updated     = order['updatedAt'],
                closed      = order['closedAt']
            ) 
            for order in response
            ]
        return orders

    async def resolve_tickers(self, info):
        response = await fetch(f'https://api.coingecko.com/api/v3/exchanges/bittrex/tickers', request_type='get')
        tickers = [Ticker(name=ticker['base'], usd=ticker['converted_last']['usd']) for ticker in response['tickers']]
        return tickers

class AddBittrexOrder(graphene.Mutation):
    class Input:
        # user_id     = graphene.String()
        marketSymbol    = graphene.String()
        direction       = graphene.String()
        type            = graphene.String()
        quantity        = graphene.Float()
        ceiling         = graphene.Float()
        limit           = graphene.Float()
        timeInForce     = graphene.DateTime()
        clientOrderId   = graphene.String()
        useAwards       = graphene.String()

    order = graphene.Field(Order)

    @staticmethod
    async def mutate(root, info, **input):
        pb = dict(
            marketSymbol    = input['marketSymbol'],
            direction       = input['direction'],
            type            = input['type'],
            quantity        = input['quantity'],
            ceiling         = input['ceiling'],
            limit           = input['limit'],
            timeInForce     = input['timeInForce'],
            clientOrderId   = input['clientOrderId'],
            useAwards       = input['useAwards'],
        )
        #TODO: Fix api keys here
        response = await gen_request(BASE_URL + f'/orders', 'post', api_secret, api_key)

        return AddBittrexOrder(pb)