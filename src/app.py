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
from starlette.applications     import Starlette
from starlette_jwt              import JWTAuthenticationBackend
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

import uvicorn
import graphene
import json
import jwt
import datetime
import bcrypt
import asyncio
import os
import time
from models         import User, Exchange, CoinGecko
from schema         import Query, Mutation
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
    user = User.objects(username=body['username']).first()

    if not user:
        raise Exception('User not found')
    
    if bcrypt.checkpw(body['password'].encode(), user.password.encode()):
        raise Exception('Wrong Username/Password')
    token = jwt.encode({'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=300), 'username':user.username}, 'secret', algorithms=['HS256']).decode('utf-8')
    response = {'token': token}
    return JSONResponse(response)


async def authenticate(msg):

    user = User.objects(username=msg['username']).first()

    if not user:
        raise Exception('User not found')
    
    if not bcrypt.checkpw(msg['password'].encode(), user.password.encode()):
        raise Exception('Wrong Username/Password')

    user.__dict__['password_decrypted'] = msg['password']
    user.__dict__['exchanges'] = {}
    for account in user.accounts:
        user.__dict__['exchanges'][account.exchange.name] = {
            'api_key': password_decrypt(account.api_key.encode('utf-8'), msg['password']).decode('utf-8'),
            'api_secret': password_decrypt(account.secret.encode('utf-8'), msg['password']).decode('utf-8')
        }

    user.__dict__['wallets'] = {}
    for wallet in user.wallets:
        user.__dict__['wallets'][wallet.wallet_type] = {
            'address': wallet.address,
            'tokens': wallet.tokens
        }

    if user.loop_state != 'running':
        asyncio.create_task(run_in_threadpool(background_process.background_user_sync, app, user))

    return user

async def WS(websocket):
    await websocket.accept()

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
                user = await authenticate(msg['payload'])
                await websocket.send_json({"id": msg['id'], "payload":"success"})
                continue
            except Exception as e:
                print(f'error during auth: {e}')
                await websocket.close()

        print(f'received: {msg}')
        app.mongo.reload()
        # if msg['payload'].lower().startswith('query') or msg['payload'].lower().startswith('\nquery'):
        result = await schema.execute(msg['payload'], executor=AsyncioExecutor(loop=asyncio.get_running_loop()), return_promise=True, context={'user': user, 'app': app})
        # else:
        #     result = schema.execute(msg['payload'], context={'user': user, 'app': app})

        if not result.data and result.errors:
            await websocket.send_json({"id": msg['id'], "error": result.errors[0]})

        await websocket.send_json({"id": msg['id'], "payload": result.data})
    await websocket.close()

# class DBMiddleware:
#     async def resolve(self, next, root, info, **args):
#         start = time.time()
#         results = next(root, info, **args)
#         # coin_gecko = info.context['request'].app.mongo.coin_gecko.find_one()
#         # info.context['coin_gecko'] = coin_gecko
#         print(f'request {time.time() - start}s')
#         return results

routes = [
    Route('/', helloworld),
    Route('/login', login, methods=['POST']),
    WebSocketRoute('/ws', WS),
    Route('/graphql', GraphQLApp(schema=schema, executor_class=AsyncioExecutor))
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
    Middleware(AuthenticationMiddleware, backend=JWTAuthenticationBackend(secret_key='secret', prefix='JWT'))
]

def on_startup():
    coin_gecko = CoinGecko.objects().first()
    if coin_gecko.loop_state != 'running':
        coin_gecko.loop_state = 'running'
        coin_gecko.save()
    
    for user in User.objects():
        user.loop_state = 'stopped'
        user.save()

    asyncio.ensure_future(background_process.coin_gecko())

def on_shutdown():
    coin_gecko = CoinGecko.object().first()
    coin_gecko.loop_state = 'stopped'
    coin_gecko.save()

app = Starlette(debug=True, routes=routes, middleware=middleware, on_startup=[on_startup], on_shutdown=[on_shutdown])
app.__dict__['mongo'] = CoinGecko.objects().first()
print('started')

if __name__ == '__main__':
    # init_db()
    # print_schema()
    #asyncio.ensure_future(background_sync())
    uvicorn.run(app, host="0.0.0.0", port=8000)