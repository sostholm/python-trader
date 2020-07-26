from cro_websockets_api import CryptoWebsocketAPI


if __name__ == '__main__':
    api_key = os.environ['api_key']
    secret  = os.environ['secret']

    api = CryptoWebsocketAPI(key=api_key, sec=secret)
    asyncio.get_event_loop().run_until_complete(api.init_websocket())
    asyncio.get_event_loop().run_until_complete(subscribe_request(api=api))