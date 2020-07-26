from bson                       import ObjectId
from cro_websockets_api         import CryptoWebsocketAPI
from starlette.concurrency      import run_in_threadpool
import models
import datetime

all_api = {
    "CryptoWebsocketAPI": CryptoWebsocketAPI
}

def add_to_database(currencies):
    for currency in currencies.values():
        if currency.trades.count() > 10000:
            [currency.trades.remove(trade) for trade in currency.trades[:1000]]
        currency.save()

async def background_sync(exchange_id):
    exchange = models.Exchange.objects(id=ObjectId(exchange_id)).first()
    api = all_api[exchange.exchange_api]()
    await api.init_websocket()
    subscriptions = exchange.subscriptions
    req = await api.subscribe_market(instruments=subscriptions, channel='trade', method='subscribe')
    gen = api.get_request_generator(req=req, socket_type='market')

    currencies = {currency.pair: currency for currency in models.CurrencyPair.objects}

    update_count = 0

    async for candle in gen:
        for trade in candle['data']:
            
            price = int(trade['p'] *100000000)
            quantity = trade['q']
            timestamp = datetime.datetime.fromtimestamp(trade['t'] / 1000)

            trade = models.Trade(timestamp=timestamp, price=price, quantity=quantity)
            currencies[candle['instrument_name']].trades.append(trade)
            
            if update_count > 10:
                await run_in_threadpool(add_to_database, currencies)
                update_count = 0

            print(f'price: {price}s, quantity: {int(quantity)}')

            update_count += 1