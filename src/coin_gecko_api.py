import urllib
from urllib.parse import urlencode, quote_plus
import hmac
import hashlib
import time
import os
import asyncio
import requests
from functools import partial
import aiohttp
from datetime import datetime

def get_timestamp():
    ts = "%d"%int(round(time.time() * 1000))
    return ts


class CoinGeckoAPI:

    def __init__(self):
        self.timeout = 1000

    async def subscribe_to_request(self, uri, headers, frequency=5):
    
        async with aiohttp.ClientSession(headers=headers) as session:

            while True:
                start = datetime.now()
                
                async with session.get(uri) as r:
                    json_body = await r.json()
                    yield json_body
                
                while (datetime.now() - start) < frequency:
                    await asyncio.sleep(1)
        
            
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
    # api_key = os.environ['api_key']
    # secret  = os.environ['secret']

    api = CoinGeckoAPI()
    asyncio.get_event_loop().run_until_complete(api.init_websocket())
    # asyncio.get_event_loop().run_until_complete(api.balance())
    # asyncio.get_event_loop().run_until_complete(print_user_balance(api))
    # asyncio.get_event_loop().run_until_complete(asyncio.gather(print_subscription(api), print_user_trades(api)))