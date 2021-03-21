from graphql.execution.executors.asyncio    import AsyncioExecutor
from starlette.applications                 import Starlette
from starlette.responses                    import JSONResponse
from starlette.routing                      import Route, WebSocketRoute
from starlette.graphql                      import GraphQLApp
from starlette.middleware                   import Middleware
from starlette.middleware.cors              import CORSMiddleware
from starlette.applications                 import Starlette
from starlette_jwt                          import JWTAuthenticationBackend
from starlette.middleware.authentication    import AuthenticationMiddleware
from starlette.middleware.base              import BaseHTTPMiddleware
import uvicorn
import graphene
import json
import jwt
import datetime
import bcrypt
import asyncio
import os
import time
import aiohttp
from models         import User, fetch
from database       import get_client
from util           import make_wallets, make_exchanges

from schema         import Query
from encrypt        import password_decrypt
from bson           import ObjectId
from schema         import schema


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
    
    user['exchanges'] = make_exchanges(user, body['password'], exchanges)
    user['wallets'] = make_wallets(user, wallet_types)

    if user['loop_state'] != 'running':
        try:
            payload = {'_id': str(user['_id']), 'wallets': user['wallets'], 'exchanges': user['exchanges']}
            await fetch(request.app.aiohttp_session, f'http://{os.environ["WORKER"]}:8002', 'post', body={"user": payload})
        except Exception as e:
            print(e)

    token = jwt.encode({'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1800), 'id': str(user['_id']), 'access': 'write'}, 'secret', algorithm='HS256')
    response = {'token': token.decode('utf-8')}
    return JSONResponse(response)


class AuthMiddleware:
    async def resolve(self, next, root, info, **args):
        if not info.context['request']['user'].is_authenticated:
            raise Exception('Not authenticated.')
        if info.context['request']['user'].payload['access'] == 'read' and 'mutation' in json.dumps(info.context['request']._json).lower():
            raise Exception('Not authorized for mutations.')

        results = next(root, info, **args)
        return results


routes = [
    Route('/', helloworld),
    Route('/login', login, methods=['POST']),
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
    client = get_client(asyncio.get_running_loop())
    app.__dict__['mongo'] = client
    app.__dict__['aiohttp_session'] = aiohttp.ClientSession()

def on_shutdown():
    pass

app = Starlette(debug=True, routes=routes, middleware=middleware, on_startup=[on_startup], on_shutdown=[on_shutdown])
print('started')

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
