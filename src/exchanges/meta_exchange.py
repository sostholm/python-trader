from collections import UserDict
from functools import total_ordering
from os import name
import graphene
from mongoengine    import Document, EmbeddedDocument
from mongoengine    import (DateTimeField, FloatField, StringField, IntField,
ReferenceField, ListField, EmbeddedDocumentListField, DictField, BinaryField)
import asyncio
import functools
import concurrent
import logging
import exchanges
import sys

logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
log = logging.getLogger(f'meta_exchange')

class Order(graphene.ObjectType):
    side        = graphene.String()
    fee         = graphene.Float()
    created_at  = graphene.DateTime()
    deal_price  = graphene.Float()
    avg_price   = graphene.Float()
    volume      = graphene.Float()
    price       = graphene.Float()
    status_msg  = graphene.String()
    remain_volume = graphene.Float()
    baseCoin    = graphene.String()
    countCoin   = graphene.String()
    status      = graphene.Int()
    all_details = graphene.JSONString()

class Trade(EmbeddedDocument):
    quantity        = FloatField()
    trade_type      = StringField()
    price           = FloatField()
    timestamp       = DateTimeField()

class Order(graphene.ObjectType):
    id          = graphene.String()
    market      = graphene.String()
    direction   = graphene.String()
    order_type  = graphene.String()
    quantity    = graphene.String()
    limit       = graphene.String()
    timeInForce = graphene.String()
    fillQuantity= graphene.String()
    commission  = graphene.String()
    proceeds    = graphene.String()
    created     = graphene.String()
    updated     = graphene.String()
    closed      = graphene.String()

class Balance(graphene.ObjectType):
    currency        = graphene.String()
    total           = graphene.String()
    available       = graphene.String()
    updated         = graphene.String()
    usd             = graphene.String()
    exchange        = graphene.String()
    price_change_percentage_14d_in_currency     = graphene.String()
    price_change_percentage_1h_in_currency      = graphene.String()
    price_change_percentage_24h_in_currency     = graphene.String()
    price_change_percentage_30d_in_currency     = graphene.String()
    price_change_percentage_7d_in_currency      = graphene.String()

class Ticker(graphene.ObjectType):
    name        = graphene.String()
    usd         = graphene.String()

class MetaExchange(graphene.Interface):
    name            = graphene.String()
    instruments     = graphene.JSONString()
    balance         = graphene.List(Balance, api_key=graphene.String(), api_secret=graphene.String())
    orders          = graphene.List(Order, api_key=graphene.String(), api_secret=graphene.String(), order_type=graphene.String())
    tickers         = graphene.List(Ticker, api_key=graphene.String(), api_secret=graphene.String())


def update_coin_gecko(coin_gecko, not_in_coin_gecko):
    for coin in not_in_coin_gecko:
        if coin not in coin_gecko['subscriptions']:
            coin_gecko['subscriptions'].append(coin)
    coin_gecko.save()
    print('updated coin gecko')

async def coin_gecko_thread(coin_gecko, not_in_coin_gecko):
    loop = asyncio.new_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(
            pool, functools.partial(update_coin_gecko, coin_gecko, not_in_coin_gecko)
        )


def make_coins(context, balances, currency, total, available):
    if 'request' in context:
        coin_gecko = context['request'].app.mongo
    else:
        coin_gecko = context['app'].mongo

    balance = []
    not_in_coin_gecko = []

    for coins in balances:
        coin_total = 0
        if '_' in total:
            combined = total.split('_')
            coin_total = float(coins[combined[0]]) + float(coins[combined[1]])
        else:
            coin_total = float(coins[total])

        if coin_total > 0:
            usd = 0
            entries = [entry for entry in coin_gecko['coin_list'] if coins[currency].lower() == entry['symbol'].lower()]
            
            #If aave token is not found, search for it's non 'a' counterpart
            if len(entries) == 0 and coins[currency][0] == 'a':
                entries = [entry for entry in coin_gecko['coin_list'] if coins[currency].lower()[1:] == entry['symbol'].lower()]

            if len(entries) > 0:
                db_entry = entries[0]
                if db_entry:
                        usd = float(coin_total) * db_entry['current_price']

                else:
                    log.warning(f'{coins[currency]} not found in CoinGecko.coin_list!')
                
                all_fields = dict(
                    currency                                    = coins[currency], 
                    total                                       = coin_total, 
                    available                                   = coins[available], 
                    usd                                         = usd,
                    price_change_percentage_14d_in_currency     = db_entry['price_change_percentage_14d_in_currency'],
                    price_change_percentage_1h_in_currency      = db_entry['price_change_percentage_1h_in_currency'],
                    price_change_percentage_24h_in_currency     = db_entry['price_change_percentage_24h_in_currency'],
                    price_change_percentage_30d_in_currency     = db_entry['price_change_percentage_30d_in_currency'],
                    price_change_percentage_7d_in_currency      = db_entry['price_change_percentage_7d_in_currency']
                )

                balance.append(all_fields)

    # if len(not_in_coin_gecko) > 0:
        # background = context["background"]
        # background.add_task(update_coin_gecko, coin_gecko=coin_gecko, not_in_coin_gecko=not_in_coin_gecko)
        # asyncio.create_task(coin_gecko_thread(coin_gecko, not_in_coin_gecko))

    return balance