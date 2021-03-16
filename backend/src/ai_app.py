from starlette.applications import Starlette
from starlette.responses    import JSONResponse
from starlette.routing      import Route
from starlette.middleware   import Middleware
from starlette.middleware.cors  import CORSMiddleware
from starlette.applications     import Starlette
from starlette.middleware.base import BaseHTTPMiddleware

import uvicorn
import os
import time
# from async_mongo_logger import Logger

import matplotlib.pyplot as plt
import numpy as np
import tflite_runtime.interpreter as tflite

import pandas as pd
import random
import os
import cv2
from uuid import uuid4
import matplotlib
import mplfinance as mpf
matplotlib.use('Agg')

# loaded_model = tf.keras.models.load_model('/usr/models/btc_1h_80_percent')
interpreter = tflite.Interpreter(model_path='/usr/models/btc_1h_80_percent.tflite')
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
interpreter.allocate_tensors()

classes = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]

async def predict(request):
    body = await request.json()
    
    df = pd.DataFrame(body)
    df['date'] = pd.to_datetime(df[0],unit='ms')
    df.set_index(['date'], inplace=True)
    df.drop([0], axis='columns', inplace=True)
    df.rename(columns={1: "Open", 2: "High", 3: "Low", 4: "Close"}, inplace=True)

    path = f'/tmp'
    file = path+ f'/{uuid4()}.png'
    mpf.plot(df,type='candle', style='charles', axisoff=True, savefig=dict(fname=file, bbox_inches="tight"), closefig=True, returnfig=True)
    plt.close('all')

    img = cv2.imread(file, cv2.COLOR_RGBA2RGB)
    width = int(img.shape[0]* 5 / 100)
    height = int(img.shape[1]* 5 / 100)
    dim = (width, height)
    resized =cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    reshaped = np.reshape(resized, [1, 29, 21, 3])
    
    reshaped = reshaped.astype(np.float32)
    interpreter.set_tensor(input_details[0]['index'], reshaped)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    results = np.squeeze(output_data)
    
    prediction = list(results)

    prediction = classes[prediction.index(max(prediction))]
    
    os.remove(file)

    return JSONResponse({"prediction": prediction})

routes = [
    Route('/', predict, methods=['POST']),
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
    pass
    # global trader_database 
    # trader_database = get_client(asyncio.get_running_loop()).trader
    # client = get_client(asyncio.get_running_loop())
    # app.__dict__['mongo'] = client
    # logger = Logger(name='coin_gecko', client=client, database='logs', collection='trader', log_to_console=True)
    # await logger.info('Set all loops to stopped')
    # await logger.info('Started tasks')

def on_shutdown():
    pass
    # coin_gecko = CoinGecko.object().first()
    # coin_gecko.loop_state = 'stopped'
    # coin_gecko.save()

app = Starlette(debug=True, routes=routes, middleware=middleware, on_startup=[on_startup], on_shutdown=[on_shutdown])

print('started')

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8003)