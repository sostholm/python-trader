from bson                                   import ObjectId
from starlette.concurrency                  import run_in_threadpool
from graphql.execution.executors.asyncio    import AsyncioExecutor
from schema                                 import schema
import models
from datetime import datetime
import json
import aiohttp
import asyncio
import requests
import time

from web_push import send_web_push

import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# all_api = {
#     "CryptoWebsocketAPI": CryptoWebsocketAPI
# }

# async def fetch(url, request_type, body=None, headers=None):
    
#         params = {}
#         params['url']           = url
#         if body:
#             params['json']      = body
#         if headers:
#             params['headers']   = headers

#         async with getattr(session, request_type)(**params) as resp:
#             print(resp.status)
#             resp = await resp.text()
#             return json.loads(resp)


# def add_to_database(coin_gecko, prices):
#     coin_gecko.current_prices = prices
#     coin_gecko.save()

# def update_coin_gecko(coin_gecko):
#     return coin_gecko.reload()

async def coin_gecko():

    coin_gecko = models.CoinGecko.objects().first()

    coin_gecko.loop_state = 'running'
    coin_gecko.save()

    print('starting coin gecko sync...')

    try:
        # response = requests.get('https://api.coingecko.com/api/v3/coins/list').json() 
        # coins = {models.CoinGeckoCoin(**coin) for coin in response if '$' not in coin['symbol']}
        # coin_gecko.coin_list = coins
        # coin_gecko.save()



        while coin_gecko.loop_state == 'running':
            start = datetime.now()

            coin_gecko.reload()
            subscriptions = ",".join(coin_gecko.subscriptions)

            if subscriptions != '':
                # response = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={subscriptions}&vs_currencies=usd').json()
                # coin_gecko.current_prices = response
                response = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=false&price_change_percentage=1h,24h,7d,14d,30d")
                if response.ok:
                    coin_gecko.coin_list = response.json()
                coin_gecko.last_price_update = datetime.now()
                coin_gecko.save()

            while (datetime.now() - start).seconds < 60:
                coin_gecko.reload()
                if coin_gecko.loop_state != 'running':
                    break
                await asyncio.sleep(5)
    except Exception as e:
        print(e)

    coin_gecko.loop_state = 'stopped'
    coin_gecko.save()

def create_exchange_balance_query(exchange):
    return exchange + '''{
    balance{
      currency
      total
      available
      usd
      priceChangePercentage1hInCurrency
      priceChangePercentage24hInCurrency 
    }
  } 
'''

def background_user_sync(app, user):
    log = logging.getLogger(f'background_user_sync: {user.username}')
    user_with_decrypted_keys = user

    user = models.User.objects(username=user.username).first()
    loop = asyncio.new_event_loop()

    log.info(f'starting background sync for {user.username}')
    user.loop_state = "running"
    user.save()

    try:
        while user.loop_state == "running":
            start = datetime.now()
            
            app.mongo.reload()
            user.reload()

            query = ''

            if hasattr(user, 'accounts'):

                for account in user.accounts:
                    query = query +  create_exchange_balance_query(account.exchange.name)
                
                for wallet in user.wallets:
                    query = query +  create_exchange_balance_query(wallet.wallet_type.name)
                query = 'query{\n' + query + '\n}'
                
                result = loop.run_until_complete(schema.execute(query, executor=AsyncioExecutor(loop=loop), return_promise=True, context={'app': app, 'user': user_with_decrypted_keys}))
                
                if result.data:
                    
                    balance = []
                    for key in result.data.keys():
                        if result.data[key]['balance']:
                            for entry in result.data[key]['balance']:
                                entry['exchange'] = key 
                                balance.append(entry)
                    
                    user.portfolio = balance
                    
                    total_usd = sum([float(currency['usd']) for exchange in result.data.values() if exchange['balance'] for currency in exchange['balance']])
                    
                    for currency in balance:
                        
                        if currency['priceChangePercentage1hInCurrency']:
                            try:
                                change = float(currency['priceChangePercentage1hInCurrency'])

                                if change > 4.5 or change < -4.5:
                                    if (
                                            isinstance(user.events, list) and 
                                            list(filter(lambda x: x['currency'] == currency['currency'] and x['date'] == datetime.now().strftime("%Y%m%d") and x['type'] == 'priceChangePercentage1hInCurrency', user.events))
                                    ):
                                        #If an entry for this event exists, skip
                                        continue
                                    
                                    if user.subscription:
                                        try:
                                            send_web_push(user.subscription, f'{currency["currency"]} is up by {change} 1h')
                                            event = {'currency': currency['currency'], 'date': datetime.now().strftime("%Y%m%d"), 'type': 'priceChangePercentage1hInCurrency'}
                                            user.events.append(event)
                                            log.info(f'event sent for {event}')
                                        except Exception as e:
                                            log.error(e)
                            except TypeError as e:
                                log.error(f'Unable to convert priceChangePercentage1hInCurrency for {currency["currency"]}')
                        
                        if currency['priceChangePercentage24hInCurrency']:
                            try:
                                change = float(currency['priceChangePercentage24hInCurrency'])

                                if change > 4.5 or change < -4.5:
                                    if (
                                            isinstance(user.events, list) and 
                                            list(filter(lambda x: x['currency'] == currency['currency'] and x['date'] == datetime.now().strftime("%Y%m%d") and x['type'] == 'priceChangePercentage24hInCurrency', user.events))
                                    ):
                                        #If an entry for this event exists, skip
                                        continue
                                    
                                    if user.subscription:
                                        try:
                                            send_web_push(user.subscription, f'{currency["currency"]} is up by {change} 24h')
                                            event = {'currency': currency['currency'], 'date': datetime.now().strftime("%Y%m%d"), 'type': 'priceChangePercentage24hInCurrency'}
                                            user.events.append(event)
                                            log.info(f'event sent for {event}')
                                        except Exception as e:
                                            log.error(e)

                            except TypeError as e:
                                log.error(f'Unable to convert priceChangePercentage24hInCurrency for {currency["currency"]}')


                    user.total_value.append(models.TotalValue(usd_value=total_usd))
                    user.last_update = datetime.now()
                    user.save()
                
                if result.errors:
                    [log.error(error.message) for error in result.errors if hasattr(error, 'message')]

                while (datetime.now() - start).seconds < 60:
                    user.reload()
                    if user.loop_state != 'running':
                        break
                    time.sleep(5)
    except Exception as e:
        log.error(e)

    user.loop_state == "stopped"
    user.save
    
        
        

            
#         {
#   "bitcoin": {
#     "usd": 11720.89
#   }
# }