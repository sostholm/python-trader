from graphql.execution.executors.asyncio import AsyncioExecutor
from starlette.applications import Starlette
from starlette.responses    import JSONResponse, Response
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
from models         import User
from database       import get_client

from schema         import Query
from encrypt        import password_decrypt
from bson           import ObjectId
from schema         import schema
from datetime       import datetime
from multiprocessing import Process
import background_process

tasks = {}

trader_database = None

async def user_loop(request):
    global tasks
    global trader_database
    body = await request.json()

    user = body['user']
    if user['_id'] not in tasks:
        tasks[user['_id']] = asyncio.ensure_future(background_process.background_user_sync(app, body['user']))

        start = datetime.now()

        results = await trader_database.users.find_one({'_id': ObjectId(user['_id'])}, {'loop_state': True})
        state = results['loop_state']

        while state != 'running' or (start - datetime.now()).seconds > 10:

            results = await trader_database.users.find_one({'_id': ObjectId(user['_id'])}, {'loop_state': True})
            state = results['loop_state']

            if state != 'running':
                await asyncio.sleep(0.5)

    return Response()

routes = [
    Route('/', user_loop, methods=['POST']),
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
    # Middleware(AuthenticationMiddleware, backend=JWTAuthenticationBackend(secret_key='secret', prefix='JWT'))
]

async def on_startup():
    global trader_database 
    trader_database = get_client(asyncio.get_running_loop()).trader
    client = get_client(asyncio.get_running_loop())
    app.__dict__['mongo'] = client
    users = await client.trader.users.find({}, {'_id': True}).to_list(length=1000)
    for user in users:
        _id = ObjectId(user['_id'])
        await client.trader.users.update_one({'_id': _id}, {'$set': {'loop_state': 'stopped'}}, upsert=True)

    tasks['gecko'] = asyncio.ensure_future(background_process.coin_gecko())

def on_shutdown():
    pass
    # coin_gecko = CoinGecko.object().first()
    # coin_gecko.loop_state = 'stopped'
    # coin_gecko.save()

app = Starlette(debug=True, routes=routes, middleware=middleware, on_startup=[on_startup], on_shutdown=[on_shutdown])

print('started')

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8002)