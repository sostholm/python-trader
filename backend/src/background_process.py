from bson                                   import ObjectId
from starlette.concurrency                  import run_in_threadpool
from graphql.execution.executors.asyncio    import AsyncioExecutor
from schema                                 import schema
import models
from database import get_client
from datetime import datetime
import json
import aiohttp
import asyncio
import requests
import time

from util               import process_to_lower_with_underscore
from web_push           import send_web_push

from async_mongo_logger import Logger
import sys

async def update_gecko(collection, gecko, update):
    return await collection.update_one({'_id': gecko['_id']}, {'$set': update} , upsert=False)

async def update_coins(collection, updates):
    for update in updates:
        await collection.update_one({'id': update['id']}, {'$set': update}, upsert=True)

async def coin_gecko():

    client = get_client(asyncio.get_running_loop())
    logger = Logger(name='coin_gecko', client=client, database='logs', collection='trader', log_to_console=True)
    gecko_collection = client.trader.coin_gecko
    coin_gecko = await gecko_collection.find_one({})
    coins_collection = client.trader.coins

    await update_gecko(gecko_collection, coin_gecko, {'loop_state':'running'})
    coin_gecko = await gecko_collection.find_one({})

    await logger.info('starting coin gecko sync...')

    
    while coin_gecko['loop_state'] == 'running':
        start = datetime.now()
        try:
            coin_gecko = await gecko_collection.find_one({})

            subscriptions = ",".join(coin_gecko['subscriptions'])

            if subscriptions != '':

                response = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=false&price_change_percentage=1h,24h,7d,14d,30d")
                if response.ok:
                    coin_list = response.json()
                    await update_coins(coins_collection, coin_list)

                await update_gecko(gecko_collection, coin_gecko, {'last_price_update': int(datetime.now().timestamp())})

            
        except Exception as e:
            print(e)

        while (datetime.now() - start).seconds < 60:
            coin_gecko = await gecko_collection.find_one({})
            if coin_gecko['loop_state'] != 'running':
                break
            await asyncio.sleep(5)

    await update_gecko(gecko_collection, coin_gecko, {'loop_state': 'stopped'})

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

async def update_user(collection, user, update, method='$set'):
    return await collection.update_one({'_id': user['_id']}, {method: update} , upsert=False)

async def background_user_sync(app, user):
    user_with_decrypted_keys = user
 
    loop = asyncio.get_running_loop()
    client = get_client(loop)
    logger = Logger(name='background_user_sync', client=client, database='logs', collection='trader', log_to_console=True)
    user_collection = client.trader.users
    user = await user_collection.find_one({'_id': ObjectId(user['_id'])})

    await logger.info(f'starting background sync for {user["username"]}')
    
    await update_user(user_collection, user, {'loop_state': "running"})

    user = await user_collection.find_one({'_id': user['_id']})

    while user['loop_state'] == "running":
        start = datetime.now()
        
        try:
            user = await user_collection.find_one({'_id': user['_id']})

            query = ''

            if 'accounts' in user:

                for account in user['accounts']:
                    exchange = await client.trader.exchanges.find_one({'_id': account['exchange']})
                    query = query +  create_exchange_balance_query(exchange['name'])
                
                for wallet in user['wallets']:
                    wallet_type = await client.trader.wallet_types.find_one({'_id': wallet['wallet_type']})
                    query = query +  create_exchange_balance_query(wallet_type['name'])
                query = 'query{\n' + query + '\n}'
                
                result = await schema.execute(query, executor=AsyncioExecutor(loop=loop), return_promise=True, context={'app': app, 'user': user_with_decrypted_keys})
                
                if result.data:
                    
                    balance = []
                    updates = []
                    for key in result.data.keys():
                        if result.data[key]['balance']:
                            for entry in result.data[key]['balance']:
                                entry['exchange'] = key 
                                balance.append(entry)
                                updates.append(process_to_lower_with_underscore(entry))

                    await update_user(user_collection, user, {'portfolio': updates})

                    
                    total_usd = sum([float(currency['usd']) for exchange in result.data.values() if exchange['balance'] for currency in exchange['balance']])
                    
                    try:
                        await handle_notifications(user=user, balance=balance, client=client)
                    except Exception as e:
                        await logger.error(f'notification: {e.message}')
                    
                    # user.total_value.append(models.TotalValue(usd_value=total_usd))
                    await update_user(user_collection, user, {'last_update': int(datetime.now().timestamp())})
                
                if result.errors:
                    [await logger.error(error.message) for error in result.errors if hasattr(error, 'message')]
        
        except Exception as e:
            await logger.error(e)
        
        while (datetime.now() - start).seconds < 60:
            user = await user_collection.find_one({'_id': user['_id']})
            if user['loop_state'] != 'running':
                break
            time.sleep(5)
    
    await update_user(user_collection, user, {'loop_state': "stopped"})
    
        
async def handle_notifications(user, balance, client):
    up_1h       = []
    down_1h     = []
    up_24h      = []
    down_24h    = []
    date        = datetime.now().strftime("%Y%m%d")
    events_collection = client.trader.events
    

    for currency in balance:
        
        if currency['priceChangePercentage1hInCurrency']:
            change = float(currency['priceChangePercentage1hInCurrency'])
            
            if change > 5 or change < -5:
                event = await events_collection.find_one({'currency': currency['currency'], 'user': ObjectId(user['_id']), 'date': date, 'type': 'priceChangePercentage1hInCurrency'})
                if event:
                    #If an entry for this event exists, skip
                    continue
                
                elif change > 5:
                    up_1h.append(currency["currency"])
                else:
                    down_1h.append(currency["currency"])
        
        if currency['priceChangePercentage24hInCurrency']:
            change = float(currency['priceChangePercentage24hInCurrency'])

            if change > 10 or change < -10:
                event = await events_collection.find_one({'currency': currency['currency'], 'user': ObjectId(user['_id']), 'date': date, 'type': 'priceChangePercentage24hInCurrency'})
                if event:
                    #If an entry for this event exists, skip
                    continue
                
                elif change > 10:
                    up_24h.append(currency["currency"])
                else:
                    down_24h.append(currency["currency"])

        if user['subscription']:

            message = ""
            if up_1h:
                message += f'{",".join(up_1h)} is up > 5% in 1h'
            if down_1h:
                message += f'{",".join(down_1h)} is down < -5% in 1h'
            if up_24h:
                message += f'{",".join(up_24h)} is up < 10% in 24h'
            if down_24h:
                message += f'{",".join(down_24h)} is down < -10% in 24h'

            if message:
                send_web_push(user['subscription'], message)

                for currency in up_1h + down_1h:
                    event = {'currency': currency, 'date': datetime.now().strftime("%Y%m%d"), 'type': 'priceChangePercentage1hInCurrency'}
                    await events_collection.insert_one({'currency': currency, 'user': ObjectId(user['_id']), 'date': date, 'type': 'priceChangePercentage1hInCurrency'})

                for currency in up_24h + down_24h:
                    event = {'currency': currency, 'date': datetime.now().strftime("%Y%m%d"), 'type': 'priceChangePercentage24hInCurrency'}
                    await events_collection.insert_one({'currency': currency, 'user': ObjectId(user['_id']), 'date': date, 'type': 'priceChangePercentage24hInCurrency'})
            
#         {
#   "bitcoin": {
#     "usd": 11720.89
#   }
# }