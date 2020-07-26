# from crypto_dot_com_api import CryptoAPI

# if __name__ == "__main__":
#     api = CryptoAPI(api_key, secret)
#     print('attempting to print balance')
#     print(api.balance())
from graphql.execution.executors.asyncio import AsyncioExecutor
from starlette.applications import Starlette
from starlette.responses    import JSONResponse
from starlette.routing      import Route, WebSocketRoute
from starlette.graphql      import GraphQLApp
from starlette.middleware   import Middleware
from starlette.middleware.cors  import CORSMiddleware
from starlette.background       import BackgroundTask
from starlette.authentication   import requires
from starlette.concurrency      import run_in_threadpool

import uvicorn
import graphene
import json
import jwt
import datetime
import bcrypt
import asyncio
from mongoengine import connect
from models import User, CurrencyPair, Trade, Exchange
from schema import Query, Mutation
from encrypt import password_decrypt
from bson import ObjectId
# from database import init_db
from schema import schema
# from timermiddleware import TimerMiddleware
from cro_websockets_api import CryptoWebsocketAPI

connect('trader', host=f'mongodb://pine64:27017')
schema = graphene.Schema(query=Query, mutation=Mutation)



async def helloworld(request):
    return JSONResponse({'hello': 'world'})


async def login(request):
    body = await request.json()
    user = User.objects(username=body['username']).first()

    if not user:
        raise Exception('User not found')
    
    if bcrypt.checkpw(body['password'].encode(), user.password.encode()):
        raise Exception('Wrong Username/Password')
    token = jwt.encode({'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=300), 'username':user.username}, 'secret', algorithms=['HS256']).decode('utf-8')
    response = {'token': token}
    return JSONResponse(response)


async def background_user_sync(user):
    api = CryptoWebsocketAPI(key=user.api_key_decrypted, sec=user.secret_decrypted)
    
    user.loop_state = "running"
    while user.loop_state == "running":
        print('running')
        await asyncio.sleep(5)
        user = User.objects(username=user.username).first()



async def background_sync(exchange_id):
    exchange = Exchange.objects(id=ObjectId(exchange_id)).first()
    api = all_api[exchange.exchange_api]()
    await api.init_websocket()
    subscriptions = exchange.subscriptions
    req = await api.subscribe_market(instruments=subscriptions, channel='trade', method='subscribe')
    gen = api.get_request_generator(req=req, socket_type='market')

    currencies = {currency.pair: currency for currency in CurrencyPair.objects}

    update_count = 0

    async for candle in gen:
        for trade in candle['data']:
            
            price = int(trade['p'] *100000000)
            quantity = trade['q']
            timestamp = datetime.datetime.fromtimestamp(trade['t'] / 1000)

            trade = Trade(timestamp=timestamp, price=price, quantity=quantity)
            currencies[candle['instrument_name']].trades.append(trade)
            
            if update_count > 10:
                await run_in_threadpool(add_to_database, currencies)
                update_count = 0

            print(f'price: {price}s, quantity: {int(quantity)}')

            update_count += 1

def add_to_database(currencies):
    for currency in currencies.values():
        if currency.trades.count() > 10000:
            [currency.trades.remove(trade) for trade in currency.trades[:1000]]
        currency.save()

async def start_background_sync(test):
    task = BackgroundTask(background_sync)
    message = {'status': 'starting...'}
    return JSONResponse(message, background=task)
# @requires('authenticated')
# async def background_sync(request):
#     task = BackgroundTask(background_sync, api_key='key', secret='secret')
#     return JSONResponse(json.dumps(dict(success=True)), background=task)


async def authenticate(msg):

    user = User.objects(username=msg['username']).first()

    if not user:
        raise Exception('User not found')
    
    if not bcrypt.checkpw(msg['password'].encode(), user.password.encode()):
        raise Exception('Wrong Username/Password')

    if user.api_key != None and user.secret != None:
        user.__dict__['api_key_decrypted'] = password_decrypt(user.api_key, msg['password'])
        user.__dict__['secret_decrypted'] = password_decrypt(user.secret, msg['password'])
    return user

async def WS(websocket):
    await websocket.accept()
    # Process incoming messages

    msg             = ''
    user            = None

    while msg != 'close':
        try:
            msg = await websocket.receive_json()

        except Exception as e:
            print(f'error reading websocket: {e}')
            msg = 'close'
            continue

        if not user:
            try:
                user = await authenticate(msg)
                continue
            except Exception as e:
                print(f'error during auth: {e}')
                websocket.close()

        print(f'received: {msg}')
        if 'start' in msg:
            if msg['start'] == 'background_sync' and 'exchange' in msg:
                asyncio.ensure_future(background_sync(msg['exchange']))
                continue
            if msg['start'] == 'background_user_sync':
                background_sync(user, )
                continue

        result = schema.execute(msg, executor=AsyncioExecutor(loop=asyncio.get_running_loop()))
        await websocket.send_json(result)
    await websocket.close()

routes = [
    Route('/', helloworld),
    Route('/login', login, methods=['POST']),
    Route('/start_background_sync', start_background_sync),
    WebSocketRoute('/ws', WS),
    Route('/graphql', GraphQLApp(schema=schema, executor_class=AsyncioExecutor))
    ]

middleware = [
    # Middleware(TimerMiddleware),
    Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*']),
]

app = Starlette(debug=True, routes=routes, middleware=middleware)

if __name__ == '__main__':
    # init_db()
    # print_schema()
    #asyncio.ensure_future(background_sync())
    uvicorn.run(app, host="0.0.0.0", port=8000)