import urllib
from urllib.parse import urlencode, quote_plus
import hmac
import hashlib
import time
import random
import os
import json
import uuid
import asyncio
import websockets
import requests
from functools import partial


URL = 'https://api.bittrex.com/v3'

def get_timestamp():
    ts = "%d"%int(round(time.time() * 1000))
    return ts


class CryptoWebsocketAPI:

    subscriptions = {}
    responses = {}
    ws = {}

    def __init__(self, key, sec):
        self.timeout = 1000
        self.apikey = key
        self.apisec = sec
        # self.init_websocket()
        
    async def gen_base_request_params(self):
        return {
            "uri":"",
            "method":"",
            "timestamp": int(time.time() * 1000)
        } 

    def sign(self, req):

        paramString = ""

        if "params" in req: 
            for key in req['params']:
                paramString += key
                paramString += str(req['params'][key])

        sigPayload = str(req['timestamp']) + req['uri'] + str(req['method']) + paramString 

        return hmac.new(
            bytes(str(self.apisec), 'ascii'),
            msg=bytes(sigPayload, 'ascii'),
            digestmod=hashlib.sha512
        ).hexdigest()

    def set_headers(self, request):
        request['headers'] = {
            'Api-Key': self.apikey,
            'Api-Timestamp': request['timestamp'],
            'Api-Content-Hash'
        }

    def construct_request(self, request):
        request['timestamp'] = int(time.time() * 1000)
        request['signature'] = sign(request)
        request = set_headers(request)
        return request

    async def get_response(self, request):

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, partial(requests.get, data={
                url: request['uri'],
                headers: request['headers']
            })
        )

    async def subscribe_user(self, channel, method):
        req = await self.gen_base_request_params()
        req['method'] = method
        req['params'] = { "channels": [channel]}
        
        self.send_queue['user'].append(req)

        return req

    async def subscribe_to_request(self, req, socket_type, frequency=5):

        if 'response' not in locals():
            response = ''

        if 'sleep' not in locals():
            sleep = False

        while self.ws[socket_type].open:
                if sleep:
                    await asyncio.sleep(frequency)
                
                req['nonce'] = int(time.time() * 1000)
                fresh_response = await self.get_response(req, socket_type)
                
                if fresh_response == response:
                    sleep = True
                    continue
                else:
                    sleep = True
                    response = fresh_response
                    yield response

    def depth(self, sym):
        pass

    async def balance(self):
        req = await self.gen_base_request_params()
        req['uri'] = "account/balances"
        req['method'] = "GET"

        return response
        
            
async def print_subscription(api):
    #req = await api.subscribe_market(channel='candlestick.1m.CRO_BTC', method='subscribe')
    req = await api.subscribe_market(channel='trade.CRO_BTC', method='subscribe')
    gen = api.get_request_generator(req=req, socket_type='market')
    async for candle in gen:
        for trade in candle['data']:
            price = trade['p']
            quantity = trade['q']
            print(f'price: {int(price*100000000)}s, quantity: {int(quantity)}')

async def print_user_trades(api):
    req = await api.subscribe_user(channel='user.trade.BTC_CRO', method='subscribe')
    gen = api.get_request_generator(req=req, socket_type='user')
    async for response in gen:
        for trade in response['data']:
            status = trade['status']
            side = trade['side']
            price = trade['price']
            quantity = trade['quantity']
            instrument = trade['instrument_name']

            print(f'instrument: {instrument}, quantity: {quantity}, side: {side}, price: {price}')

async def print_user_balance(api):
    req = await api.subscribe_user(channel='user.balance', method='subscribe')
    gen = api.get_request_generator(req=req, socket_type='user')
    async for response in gen:
        for update in response['data']:
            print(update)


if __name__ == '__main__':
    api_key = os.environ['api_key']
    secret  = os.environ['secret']

    api = CryptoWebsocketAPI(key=api_key, sec=secret)
    asyncio.get_event_loop().run_until_complete(api.init_websocket())
    # asyncio.get_event_loop().run_until_complete(api.balance())
    # asyncio.get_event_loop().run_until_complete(print_user_balance(api))
    # asyncio.get_event_loop().run_until_complete(asyncio.gather(print_subscription(api), print_user_trades(api)))