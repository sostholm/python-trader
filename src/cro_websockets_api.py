"""
Forked from from https://crypto.com/exchange-doc#sub-api-ex-python-2
"""

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
    def __init__(self, key, sec):
        self.timeout = 1000
        self.apiurl = "https://api.crypto.com"
        self.apikey = key
        self.apisec = sec
        # self.init_websocket()


    async def disconnect(self):
        if self.ws:
            await self.ws.close()
            print('closed conneciton...')
        
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

    async def init_websocket(self):
        req = await self.gen_base_request_params()
        req["method"] = "public/auth"
        sig = self.sign(req)
        payload = req
        payload['sig'] = sig

        # async with websockets.connect('wss://stream.crypto.com/v2/user') as ws:
        #     await ws.send(json.dumps(payload))

        #     response = await ws.recv()
        #     print(response)

        #     await self.subscribe_trade(ws)
        self.ws = await websockets.client.connect('wss://stream.crypto.com/v2/user')
        await self.ws.send(json.dumps(payload))
        response = await self.ws.recv()
        print(response)
        

    async def subscribe_market(self, ws):

        req = await self.gen_base_request_params()
        req['method'] = "public/get-instruments"
        # req['params'] = dict(
        #     channels=["ticker.CRO_BTC"]
        # )
        await ws.send(json.dumps(req))

        response = await ws.recv()
        print(response)


    async def subscribe_trade(self, ws):

        req = await self.gen_base_request_params()
        req['method'] = "subscribe"
        req['params'] = { "channels": ["trade.MCO_BTC"]}

        await ws.send(json.dumps(req))

        response = await ws.recv()
        print(response)


    def http_get(self, url, params):
        headers = {
            'Content-Type': "application/x-www-form-urlencoded"
        }
        data = urlencode(params or {})
        try:
            response = requests.get(url, data, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"code": -1, "msg": "response status:%s" % response.status_code}
        except Exception as e:
            print("httpGet failed, detail is:%s" % e)
            return {"code": -1, "msg": e}

    def http_post(self, url, params):
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
        }
        data = urlencode(params or {})
        try:
            response = requests.post(url, data, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"code": -1, "msg": "response status:%s" % response.status_code}
        except Exception as e:
            print("httpPost failed, detail is:%s" % e)
            return {"code": -1, "msg": e}

    def api_key_get(self, url, params):
        if not params:
            params = {}
        params["api_key"] = self.apikey
        params["time"] = get_timestamp()
        params["sign"] = self.create_sign(params)
        return self.http_get(url, params)

    def api_key_post(self, url, params):
        if not params:
            params = {}
        params["api_key"] = self.apikey
        params["time"] = get_timestamp()
        params["sign"] = self.create_sign(params)
        return self.http_post(url, params)

    def create_sign(self, params):
        sorted_params = sorted(params.items(), key=lambda d: d[0], reverse=False)
        s = "".join(map(lambda x: str(x[0]) + str(x[1] or ""), sorted_params)) + self.apisec
        h = hashlib.sha256(s.encode('utf-8'))
        return h.hexdigest()

    def depth(self, sym):
        pass

    def balance(self):
        pass

    def get_all_orders(self, sym):
        pass

    def get_order(self, sym, oid):
        pass

    def get_ordst(self, sym, oid):
        
        # if ('code' in res) and (res['code']=='0') and ('order_info' in res['data']):
        #     return res['data']['order_info']['status']
        # return -1
        pass

    def get_open_orders(self, sym):
        pass

    def get_trades(self, sym):
        pass

    def cancel_order(self, sym, oid):
        pass

    def cancel_order_all(self, sym):
        pass


    def create_order(self, sym, side, prx, qty):
        pass
            


if __name__ == '__main__':
    api_key = os.environ['api_key']
    secret  = os.environ['secret']

    api = CryptoWebsocketAPI(key=api_key, sec=secret)
    asyncio.get_event_loop().run_until_complete(api.init_websocket())
    asyncio.get_event_loop().run_until_complete(api.disconnect())