from aiohttp.client import request
import graphene
import aiohttp
import json
from .meta_exchange import MetaExchange, Ticker, Balance, Order, make_coins
import time
import hashlib
import hmac

BASE_URL = 'https://api.bittrex.com/v3'

def gen_headers(content_hash, signature, api_key, timestamp):
    return {
        "Api-Key": api_key,
        "Api-Timestamp": str(timestamp),
        "Api-Content-Hash": content_hash,
        "Api-Signature": signature
    }

def get_content_hash(body):
    if body != '':
        body = json.dumps(body)
    return hashlib.sha512(body.encode()).hexdigest()

def sign(uri, method, apisec, timestamp, content_hash):

    sigPayload = str(timestamp) + uri + method.upper() + content_hash

    return hmac.new(
        apisec.encode(),
        msg=sigPayload.encode(),
        digestmod=hashlib.sha512
    ).hexdigest()

async def gen_request(uri, method, api_secret, api_key, body=""):
    timestamp = int(time.time() * 1000)
    content_hash = get_content_hash(body)
    signature = sign(uri=uri, method=method, timestamp=timestamp, content_hash=content_hash, apisec=api_secret)
    headers = gen_headers(content_hash, signature, api_key, timestamp)
    return await fetch(uri, method, body, headers)

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

class Bittrex(graphene.ObjectType):
    class Meta:
        interfaces = (MetaExchange,)

    async def resolve_balance(self, info, api_key="", api_secret=""):

        if api_key == "":
            api_key = info.context['user'].exchanges['bittrex']['api_key']
        if api_secret == "":
            api_secret = info.context['user'].exchanges['bittrex']['api_secret']

        response = await gen_request(BASE_URL + '/balances', 'get', api_secret, api_key)
        # balance = [
        #     Balance(currency=balance['currencySymbol'], total=balance['total'], available=balance['available'], updated=balance['updatedAt']) 
        #     for balance in response if balance['total'] > 0
        # ]
        if 'code' in response and response['code'] == 'APIKEY_INVALID':
            raise Exception("APIKEY_INVALID")
        
        return make_coins(info.context, response, 'currencySymbol', 'total', 'available') 

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
        api_key         = graphene.String()
        api_secret      = graphene.String()
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
        
        response = await gen_request(BASE_URL + f'/orders', 'post', input['api_secret'], input['api_key'])

        return AddBittrexOrder(pb)