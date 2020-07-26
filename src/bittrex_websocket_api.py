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
            "H":"c3",
            "M":"",
            "A":[],
            "I":random.randint(0,1000000000)
        }

    async def get_auth_request(self):
        req = await self.gen_base_request_params()
        timestamp = int(time.time() * 1000)
        rand_payload = uuid.uuid4()
        signature = self.sign(timestamp, rand_payload)
        req["A"] = [
            self.api_key,
            timestamp,
            rand_payload,
            signature
        ]
        req['M'] = 'Authenticate'
        return req     

    def sign(self, timestamp, random_content):

        sigPayload = str(timestamp) + random_content

        return hmac.new(
            bytes(str(self.apisec), 'ascii'),
            msg=bytes(sigPayload, 'ascii'),
            digestmod=hashlib.sha512
        ).hexdigest()

    async def init_websocket(self):

        req = self.get_auth_request()
        self.ws = await websockets.client.connect('https://socket-v3.bittrex.com/signalr')
        await self.ws.send(json.dumps(req))
        response = await self.ws.recv()
        print(response)

        self.send_queue = []

        asyncio.ensure_future(self.send_loop())
        asyncio.ensure_future(self.receive_loop())
        
    async def send_loop(self):
        while self.ws.open:
            while len(self.send_queue) > 0:
                next_request = self.send_queue.pop()
                print(f'sending request: {next_request}')
                await self.ws.send(json.dumps(next_request))
            await asyncio.sleep(0.5)
        
    async def receive_loop(self):
        while self.ws.open:
            received = json.loads(await self.ws.recv())
            print(f'received: {received}')
            if 'method' in received and received['method'] == 'public/heartbeat':
                self.send_queue.append({"id": received['id'], "method": 'public/respond-heartbeat'})

            if 'id' in received:
                self.responses[received['id']] = received
            else:
                self.responses[received['result']['subscription']] = received['result']

    async def get_response(self, request):

        while request['id'] not in self.responses:
            await asyncio.sleep(0.5)
        
        return self.responses[request['id']]

    async def subscribe_user(self, channel, method):
        req = await self.gen_base_request_params()
        req['method'] = method
        req['params'] = { "channels": [channel]}
        
        self.send_queue['user'].append(req)

        return req

    async def subscribe_market(self, channel, method):
        req = await self.gen_base_request_params()
        req['method'] = method
        req['params'] = { "channels": [channel]}
        del req['api_key']
        
        self.send_queue['market'].append(req)

        return req

    async def get_request_generator(self, req, socket_type):
        if 'response' not in locals():
            response = ''

        while self.ws[socket_type].open:
            while req['params']['channels'][0] not in self.responses or self.responses[req['params']['channels'][0]] == response:
                await asyncio.sleep(0.5)
            
            response = self.responses[req['params']['channels'][0]]
            yield response

    def depth(self, sym):
        pass

    async def balance(self):
        req = await self.gen_base_request_params()
        req['method'] = "private/get-account-summary"
        req['params'] = {}

        self.send_queue['user'].append(req)
        response = await self.get_response(req)
        print(response)
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