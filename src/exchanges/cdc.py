from aiohttp.client import request
import graphene
import aiohttp
import json
from .meta_exchange import MetaExchange, Ticker, Balance, Order, make_coins
import time
import hashlib
import hmac
import random

BASE_URL = 'https://api.crypto.com/v2/'
API_KEY = ''
API_SECRET = ''

def sign(req, api_secret):
    paramString = ""

    if "params" in req: 
        for key in req['params']:
            paramString += key
            paramString += str(req['params'][key])

    sigPayload = req['method'] + str(req['id']) + req['api_key'] + paramString + str(req['nonce'])

    sig = hmac.new(
        bytes(str(api_secret), 'utf-8'),
        msg=bytes(sigPayload, 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    req['sig'] = sig
    return req

async def gen_request(uri, method, request_type, api_secret, api_key, body=None):
    req = {
        "id": random.randint(0,1000000000),
        "method": request_type,
        "api_key": api_key,
        "params": body if body else {},
        "nonce": int(time.time() * 1000)
    }

    req = sign(req, api_secret)
    return await fetch(uri, method, req)

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
            if "Crypto.com Exchange is conducting system maintenance" in resp:
                raise Exception('Cdc is unavailable')
            return json.loads(resp)

class Cdc(graphene.ObjectType):
    class Meta:
        interfaces = (MetaExchange,)

    async def resolve_balance(self, info, api_key="", api_secret=""):
        tic = time.perf_counter()
        if api_key == "":
            api_key = info.context['user'].exchanges['cryptoCdc']['api_key']
        if api_secret == "":
            api_secret = info.context['user'].exchanges['cryptoCdc']['api_secret']

        response = await gen_request(BASE_URL + "private/get-account-summary", 'post', request_type="private/get-account-summary", api_secret=api_secret, api_key=api_key)
             
        coins = make_coins(info.context, response['result']['accounts'], 'currency', 'balance', 'available')
        toc = time.perf_counter()
        print(f'cdc, balance: {round(toc-tic, 2)}s')
        return coins

    async def resolve_orders(self, info, api_key, api_secret, order_type=""):
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