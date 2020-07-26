import urllib
from urllib.parse import urlencode, quote_plus
import hmac
import hashlib
import time
import random
import os
import json

import asyncio
import websockets


def get_timestamp():
    ts = "%d"%int(round(time.time() * 1000))
    return ts


class CryptoWebsocketAPI:

    subscriptions = {}
    responses = {}
    send_queue = {}
    ws = {}

    def __init__(self, key='', sec=''):
        self.timeout = 1000
        self.apikey = key
        self.apisec = sec
        self.running= True
        # self.init_websocket()
        
    async def gen_base_request_params(self):
        return {
            "id": random.randint(0,1000000000),
            "method": "",
            "api_key": self.apikey,
            "nonce": int(time.time() * 1000)
        }
    
    def sign(self, req):
        paramString = ""

        if "params" in req: 
            for key in req['params']:
                paramString += key
                paramString += str(req['params'][key])

        sigPayload = req['method'] + str(req['id']) + req['api_key'] + paramString + str(req['nonce'])

        return hmac.new(
            bytes(str(self.apisec), 'utf-8'),
            msg=bytes(sigPayload, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

    async def auth_request(self):
        req = await self.gen_base_request_params()
        req["method"] = "public/auth"
        sig = self.sign(req)
        payload = req
        payload['sig'] = sig
        return req

    async def init_websocket(self):
        req = await self.gen_base_request_params()
        req["method"] = "public/auth"
        sig = self.sign(req)
        payload = req
        payload['sig'] = sig

        self.ws['market'] = await websockets.client.connect('wss://stream.crypto.com/v2/market')
        self.send_queue['market'] = []
        asyncio.ensure_future(self.send_loop('market'))
        asyncio.ensure_future(self.receive_loop('market'))

        if self.apikey != '' and self.apisec != '':

            self.ws['user'] = await websockets.client.connect('wss://stream.crypto.com/v2/user')
            await self.ws['user'].send(json.dumps(payload))
            response = await self.ws['user'].recv()
            print(response)
            self.send_queue['user'] = []

            asyncio.ensure_future(self.send_loop('user'))
            asyncio.ensure_future(self.receive_loop('user'))

        
        
    async def send_loop(self, socket_type):
        while self.ws[socket_type].open:
            while len(self.send_queue[socket_type]) > 0:
                next_request = self.send_queue[socket_type].pop()
                print(f'sending request: {next_request}')
                await self.ws[socket_type].send(json.dumps(next_request))
            await asyncio.sleep(0.5)
        
    async def receive_loop(self, socket_type):
        while self.running:
            # code = 1006 (connection closed abnormally [internal]), no reason
            if not self.ws[socket_type].open:
                if socket_type == 'market':
                    self.ws['market'] = await websockets.client.connect('wss://stream.crypto.com/v2/market', ping_interval=None)
                else:
                    self.ws['user'] = await websockets.client.connect('wss://stream.crypto.com/v2/user', ping_interval=None)
                    await self.ws['user'].send(json.dumps(self.auth_request()))
            
            try:
                received = json.loads(await self.ws[socket_type].recv())
                
                print(f'received: {received}')
                if 'method' in received and received['method'] == 'public/heartbeat':
                    self.send_queue[socket_type].append({"id": received['id'], "method": 'public/respond-heartbeat'})

                if 'id' in received:
                    self.responses[received['id']] = received
                else:
                    self.responses[received['result']['subscription']] = received['result']
            
            except websockets.exceptions.ConnectionClosed:
                print('connection closed...')
                self.running = False

    async def get_response(self, request, socket_type):
        self.send_queue[socket_type].append(request)

        while request['id'] not in self.responses:
            await asyncio.sleep(0.5)
        
        return self.responses[request['id']]

    async def subscribe_user(self, channel, method):
        req = await self.gen_base_request_params()
        req['method'] = method
        req['params'] = { "channels": [channel]}
        
        self.send_queue['user'].append(req)

        return req

    async def subscribe_market(self, instruments, channel, method):
        if not isinstance(instruments, list):
            instruments = [instruments]

        req = await self.gen_base_request_params()
        req['method'] = method

        channels = [f"{channel}.{instrument}" for instrument in instruments]    
        req['params'] = { "channels": channels}
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

    async def balance(self):
        req = await self.gen_base_request_params()
        req['method'] = "private/get-account-summary"
        req['params'] = {}

        
        return req
        
    async def get_all_open_orders(self, instrument_name='', page_size=20, page=0):
        req = await self.gen_base_request_params()
        req['method'] = "private/get-open-orders"
        req['params'] = {}

        if instrument_name != '':
            req['params'] = {
                'instrument_name': instrument_name,
                'page_size': page_size,
                'page': page
            }

        return req

    async def get_order_details(self, oid):
        req = await self.gen_base_request_params()
        req['method'] = "private/get-open-orders"
        req['params'] = {'order_id':oid}

        return req

    async def get_trades(self, instrument_name='', start=None, end=None, page_size=20, page=0):
        req = await self.gen_base_request_params()
        req['method'] = "private/get-open-orders"
        req['params'] = {
            'instrument_name': instrument_name,
            'page_size': page_size,
            'page': page,
            'start_ts': start,
            'end_ts': end
        }

        if instrument_name != '':
            req['params']['instrument_name'] = instrument_name

        return req

    async def cancel_all_orders(self, instrument_name):
        req = await self.gen_base_request_params()
        req['method'] = "private/cancel-all-orders"
        req['params'] = {'instrument_name': instrument_name}

        return req

    async def cancel_order(self, instrument_name, order_id):
        req = await self.gen_base_request_params()
        req['method'] = "private/cancel-order"
        req['params'] = {
            'instrument_name': instrument_name,
            'order_id': order_id
        }

        return req

    async def create_order(self, instrument_name, side, order_type, price, quantity, client_oid=None):
        req = await self.gen_base_request_params()
        req['method'] = "private/cancel-order"
        req['params'] = {
            'instrument_name': instrument_name,
            'side': side,
            'type': order_type,
            'price': price,
            'quantity': quantity,
        }

        if client_oid:
            req['params']['client_oid'] = client_oid

        return req
            
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
    req = await api.subscribe_user(channel='user.trade', method='subscribe')
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


async def subscribe_request(api):
    req = await api.get_all_open_orders()
    gen = api.subscribe_to_request(req=req, socket_type='user')
    async for response in gen:
        print('open orders changed: '+ str(response))

if __name__ == '__main__':
    api_key = os.environ['api_key']
    secret  = os.environ['secret']

    api = CryptoWebsocketAPI(key=api_key, sec=secret)
    asyncio.get_event_loop().run_until_complete(api.init_websocket())
    asyncio.get_event_loop().run_until_complete(subscribe_request(api=api))
    # asyncio.get_event_loop().run_until_complete(api.balance())
    # asyncio.get_event_loop().run_until_complete(api.get_all_open_orders())
    # asyncio.get_event_loop().run_until_complete(print_user_balance(api))
    #asyncio.get_event_loop().run_until_complete(asyncio.gather(print_subscription(api), print_user_trades(api)))