from aiohttp.client import request
import graphene
import aiohttp
import json
from .meta_exchange import MetaExchange, Ticker, Balance, Order, make_coins
import time
import hashlib
import hmac

HOST = "https://api.gateio.ws"
PREFIX = "/api/v4"

def gen_sign(method, url, key, secret, query_string=None, payload_string=None):
    t = time.time()
    m = hashlib.sha512()
    m.update((payload_string or "").encode('utf-8'))
    hashed_payload = m.hexdigest()
    s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
    sign = hmac.new(secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
    return {'KEY': key, 'Timestamp': str(t), 'SIGN': sign}

async def gen_request(uri, method, api_secret, api_key, query_param=""):
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    sign_headers = gen_sign(method.upper(), PREFIX + uri, api_key, api_secret, query_param)
    headers.update(sign_headers)
    return await fetch(HOST + PREFIX + uri, method, query_param, headers)

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

class GateIO(graphene.ObjectType):
    class Meta:
        interfaces = (MetaExchange,)

    async def resolve_balance(self, info, api_key="", api_secret=""):
        tic = time.perf_counter()
        if api_key == "":
            api_key = info.context['user'].exchanges['gateio']['api_key']
        if api_secret == "":
            api_secret = info.context['user'].exchanges['gateio']['api_secret']

        response = await gen_request('/spot/accounts', 'get', api_secret, api_key)

        if 'label' in response and response['label'] == 'INVALID_KEY':
            raise Exception('Invalid key provided')

        coins = make_coins(info.context, response, 'currency', 'available_locked', 'available')
        toc = time.perf_counter()
        print(f'gateio, balance: {round(toc-tic, 2)}s')
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
        response = await fetch(f'https://api.coingecko.com/api/v3/exchanges/gateio/tickers', request_type='get')
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