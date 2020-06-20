# from crypto_dot_com_api import CryptoAPI

# if __name__ == "__main__":
#     api = CryptoAPI(api_key, secret)
#     print('attempting to print balance')
#     print(api.balance())

from starlette.applications import Starlette
from starlette.responses    import JSONResponse
from starlette.routing      import Route
from starlette.graphql      import GraphQLApp
from starlette.middleware   import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn

# from database import init_db
from schema import schema
# from timermiddleware import TimerMiddleware


async def helloworld(request):
    return JSONResponse({'hello': 'world'})

routes = [
    Route('/', helloworld),
    Route('/graphql', GraphQLApp(schema=schema))
    ]

middleware = [
    # Middleware(TimerMiddleware),
    Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
]

app = Starlette(debug=True, routes=routes, middleware=middleware)

if __name__ == '__main__':
    # init_db()
    # print_schema()
    uvicorn.run(app, host="0.0.0.0", port=8000)