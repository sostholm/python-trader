from graphql.execution.executors.asyncio import AsyncioExecutor
from starlette.applications import Starlette
from starlette.responses    import JSONResponse
from starlette.routing      import Route, WebSocketRoute
from starlette.graphql      import GraphQLApp
from starlette.middleware   import Middleware
from starlette.middleware.cors  import CORSMiddleware
from starlette.background       import BackgroundTask
# from starlette.authentication   import requires
from starlette.concurrency      import run_in_threadpool
from starlette.applications     import Starlette
from starlette_jwt              import JWTAuthenticationBackend
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.authentication import requires
import uvicorn
import graphene
import json
import jwt
import datetime
import bcrypt
import asyncio
import os
import time
from models         import User, fetch
from database       import get_client

from schema         import Query
# , Mutation
from encrypt        import password_decrypt
from bson           import ObjectId
# from database import init_db
from schema         import schema
# from timermiddleware import TimerMiddleware
import background_process

# connect('trader', host=f'mongodb://pine64:27017', username='root', password=os.environ["PASSWORD"], authentication_source='admin')

# schema = graphene.Schema(query=Query, mutation=Mutation)

# loop = asyncio.get_event_loop()
# client = MongoClient(f'mongodb://root:{os.environ["PASSWORD"]}@pine64:27017')
# db = client.trader

async def helloworld(request):
    return JSONResponse({'hello': 'world'})


async def login(request):
    body = await request.json()

    client = get_client(asyncio.get_running_loop())

    user = await client.trader.users.find_one({'username': body['username']})
    exchanges = await client.trader.exchanges.find({}).to_list(length=100)
    wallet_types = await client.trader.wallet_types.find({}).to_list(length=100)

    if not user:
        raise Exception('User not found')
    
    if not bcrypt.checkpw(body['password'].encode(), user['password'].encode()):
        raise Exception('Wrong Username/Password')

    user['password_decrypted'] = body['password']
    user['exchanges'] = {}
    for account in user['accounts']:
        exchange_name = [e['name'] for e in exchanges if e['_id'] == account['exchange']][0]
        user['exchanges'][exchange_name] = {
            'api_key': password_decrypt(account['api_key'].encode('utf-8'), body['password']).decode('utf-8'),
            'api_secret': password_decrypt(account['secret'].encode('utf-8'), body['password']).decode('utf-8')
        }

    wallets = {}
    for wallet in user['wallets']:
        wallet_type = [w['name'] for w in wallet_types if w['_id'] == wallet['wallet_type']][0]
        wallets[wallet_type] = {
            'address': wallet['address'],
            'tokens': wallet['tokens']
        }

    user['wallets'] = wallets

    if user['loop_state'] != 'running':
        try:
            payload = {'_id': str(user['_id']), 'wallets': user['wallets'], 'exchanges': user['exchanges']}
            await fetch('http://ptrader-worker:8002', 'post', body={"user": payload})
        except Exception as e:
            print(e)

    token = jwt.encode({'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1800), 'id': str(user['_id'])}, 'secret', algorithm='HS256')
    response = {'token': token}
    return JSONResponse(response)


async def authenticate(msg, client):

    user = await client.trader.users.find_one({'username': msg['username']})
    exchanges = await client.trader.exchanges.find({}).to_list(length=100)
    wallet_types = await client.trader.wallet_types.find({}).to_list(length=100)

    if not user:
        raise Exception('User not found')
    
    if not bcrypt.checkpw(msg['password'].encode(), user['password'].encode()):
        raise Exception('Wrong Username/Password')

    user['password_decrypted'] = msg['password']
    user['exchanges'] = {}
    for account in user['accounts']:
        exchange_name = [e['name'] for e in exchanges if e['_id'] == account['exchange']][0]
        user['exchanges'][exchange_name] = {
            'api_key': password_decrypt(account['api_key'].encode('utf-8'), msg['password']).decode('utf-8'),
            'api_secret': password_decrypt(account['secret'].encode('utf-8'), msg['password']).decode('utf-8')
        }

    wallets = {}
    for wallet in user['wallets']:
        wallet_type = [w['name'] for w in wallet_types if w['_id'] == wallet['wallet_type']][0]
        wallets[wallet_type] = {
            'address': wallet['address'],
            'tokens': wallet['tokens']
        }

    user['wallets'] = wallets

    if user['loop_state'] != 'running':
        try:
            payload = {'_id': str(user['_id']), 'wallets': user['wallets'], 'exchanges': user['exchanges']}
            await fetch('http://localhost:8001', 'post', body={"user": payload})
        except Exception as e:
            print(e)
    return user

async def WS(websocket):
    await websocket.accept()

    msg             = ''
    user            = None
    client = get_client(asyncio.get_running_loop())

    while msg != 'close':
        try:
            msg = await websocket.receive_json()

        except Exception as e:
            print(f'error reading websocket: {e}')
            msg = 'close'
            continue

        if not user:
            try:
                user = await authenticate(msg['payload'], client)
                await websocket.send_json({"id": msg['id'], "payload":"success"})
                continue
            except Exception as e:
                print(f'error during auth: {e}')
                await websocket.close()

        print(f'received: {msg}')
        # if msg['payload'].lower().startswith('query') or msg['payload'].lower().startswith('\nquery'):
        result = await schema.execute(msg['payload'], executor=AsyncioExecutor(loop=asyncio.get_running_loop()), return_promise=True, context={'user': user, 'client': client})
        # else:
        #     result = schema.execute(msg['payload'], context={'user': user, 'app': app})

        if not result.data and result.errors:
            await websocket.send_json({"id": msg['id'], "error": result.errors[0].message})

        await websocket.send_json({"id": msg['id'], "payload": result.data})
    await websocket.close()

class AuthMiddleware:
    async def resolve(self, next, root, info, **args):
        if not info.context['request']['user'].is_authenticated:
            raise Exception('Not authenticated.')
        results = next(root, info, **args)
        return results


routes = [
    Route('/', helloworld),
    Route('/login', login, methods=['POST']),
    WebSocketRoute('/ws', WS),
    Route('/graphql', GraphQLApp(schema=schema, executor_class=AsyncioExecutor, middleware=[AuthMiddleware()]))
    ]

class TimerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        tic = time.perf_counter()
        response = await call_next(request)
        toc = time.perf_counter()
        print(f'{round(toc-tic, 2)}s')
        return response

middleware = [
    Middleware(TimerMiddleware),
    Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*']),
    Middleware(AuthenticationMiddleware, backend=JWTAuthenticationBackend(secret_key='secret', prefix='Bearer', username_field='id'))
]

async def on_startup():
    # pass
    client = get_client(asyncio.get_running_loop())
    app.__dict__['mongo'] = client
    # # coin_gecko = CoinGecko.objects().first()
    # # if coin_gecko.loop_state != 'running':
    # #     coin_gecko.loop_state = 'running'
    # #     coin_gecko.save()
    
    # # for user in User.objects():
    # #     user.loop_state = 'stopped'
    # #     user.save()
    # users = await client.trader.users.find({}, {'_id': True}).to_list(length=1000)
    # for user in users:
    #     _id = ObjectId(user['_id'])
    #     await client.trader.users.update_one({'_id': _id}, {'$set': {'loop_state': 'stopped'}}, upsert=True)

    # asyncio.ensure_future(background_process.coin_gecko())

def on_shutdown():
    pass
    # coin_gecko = CoinGecko.object().first()
    # coin_gecko.loop_state = 'stopped'
    # coin_gecko.save()

app = Starlette(debug=True, routes=routes, middleware=middleware, on_startup=[on_startup], on_shutdown=[on_shutdown])
# app.__dict__['mongo'] = get_client(asyncio.get_running_loop())
print('started')

if __name__ == '__main__':
    # init_db()
    # print_schema()
    #asyncio.ensure_future(background_sync())
    uvicorn.run(app, host="0.0.0.0", port=8000)
