import json
import os
from asyncio import events
from datetime import date, datetime
from os import name

import aiohttp
import graphene
from graphene import DateTime, Field, JSONString, List, ObjectType, String, Int, Float, Enum
from graphene.relay import Node
from graphene_mongo import MongoengineConnectionField, MongoengineObjectType
from mongoengine import (BinaryField, DateTimeField, DictField, Document,
                         EmbeddedDocument, EmbeddedDocumentListField,
                         FloatField, IntField, ListField, ReferenceField,
                         StringField, connect)

import motor.motor_asyncio
from util import get_secret
# from exchanges import Balance

COIN_GECKO = 'https://api.coingecko.com/api/v3'

PASSWORD = None

if 'PASSWORD' in os.environ:
    PASSWORD = os.environ["PASSWORD"]
else:
    PASSWORD = get_secret('mongo_password').replace('\n', '')
    # with open('/run/secrets/db_password', 'r') as file:
    #     PASSWORD = file.read().replace('\n', '')


connect('trader', host=f'mongodb://{os.environ["DATABASE_HOSTNAME"]}:27017', username='root', password=PASSWORD, authentication_source='admin')
client = motor.motor_asyncio.AsyncIOMotorClient()

async def fetch(session, url, type='get', body={}):
    if type == 'get':
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(resp.reason)
            resp = await resp.text()
            return json.loads(resp)

    if type == 'post':
        async with session.post(url, json=body) as resp:
            if resp.status != 200:
                raise Exception(resp.reason)
            resp = await resp.text()
            return json.loads(resp)


class Position(ObjectType):
    # currency_pair   = ReferenceField('CurrencyPair')
    held_currency   = String()
    amount          = Float()
    date            = DateTime()
    type            = String()
    full_info       = JSONString()

class Exchange(ObjectType):
    # meta            = {'collection': 'exchanges'}
    name            = String()

class Order(graphene.ObjectType):
    id          = graphene.String()
    market      = graphene.String()
    direction   = graphene.String()
    order_type  = graphene.String()
    quantity    = graphene.Float()
    limit       = graphene.Float()
    timeInForce = graphene.Int()
    fillQuantity= graphene.Float()
    commission  = graphene.Float()
    proceeds    = graphene.Float()
    created     = graphene.DateTime()
    updated     = graphene.DateTime()
    closed      = graphene.DateTime()
    all_details = graphene.JSONString()
    exchange    = Field(Exchange)

class CoinGeckoCoin(Document):
    id                              = StringField(),
    symbol                          = StringField(),
    name                            = StringField(),
    image                           = StringField(),
    current_price                   = FloatField(),
    market_cap                      = FloatField(),
    market_cap_rank                 = IntField(),
    fully_diluted_valuation         = IntField(),
    total_volume                    = IntField(),
    high_24h                        = FloatField(),
    low_24h                         = FloatField(),
    price_change_24h                = FloatField(),
    price_change_percentage_24h     = FloatField(),
    market_cap_change_24h           = IntField(),
    market_cap_change_percentage_24h= FloatField(),
    circulating_supply              = IntField(),
    total_supply                    = IntField(),
    max_supply                      = IntField(),
    ath                             = FloatField(),
    ath_change_percentage           = FloatField(),
    ath_date                        = DateTimeField(),
    atl                             = FloatField(),
    atl_change_percentage           = FloatField(),
    atl_date                        = DateTimeField(),
    roi                             = DictField(default={}),
    last_updated                    = DateTimeField()
    price_change_percentage_14d_in_currency     = FloatField(),
    price_change_percentage_1h_in_currency      = FloatField(),
    price_change_percentage_24h_in_currency     = FloatField(),
    price_change_percentage_30d_in_currency     = FloatField(),
    price_change_percentage_7d_in_currency      = FloatField()

class State(Enum):
    start   = 1
    running = 2
    stop    = 3
    stopped = 4

class CoinGecko(ObjectType):
    last_price_update   = DateTime()
    # current_prices      = DictField(default={})
    coin_list           = List(JSONString)
    subscriptions       = List(String)
    loop_state          = Field(State)

class Account(ObjectType):
    api_key         = String()
    secret          = String()
    exchange        = Field(Exchange)
    subscriptions   = List(String)
    positions       = List(Position)
    position_history= List(Position)

class WalletType(ObjectType):
    name = String()

class Wallet(ObjectType):
    # meta            = {'collection': 'wallets'}
    name            = String()
    address         = String()
    wallet_type     = Field(WalletType)
    tokens          = List(String)

class Event(ObjectType):
    currency = String()
    date     = String()
    type     = String()

class UserBalance(ObjectType):
    currency                                = String()
    coin_id                                 = String()
    total                                   = Float()
    available                               = Float()
    usd                                     = Float()
    price_change_percentage1h_in_currency   = Float()
    price_change_percentage24h_in_currency  = Float()
    price_change_percentage7d_in_currency   = Float()
    exchange                                = String()

class User(ObjectType):
    # meta            = {'collection': 'users'}
    username        = String()
    password        = String()
    last_update     = Int()
    portfolio       = List(UserBalance, coin_id=graphene.String())
    subscription    = JSONString()
    loop_state      = String()
    accounts        = List(Account)
    wallets         = List(Wallet)
    events          = List(Event)
    portfolio_value = Float()

class ValueHistoryEntry(ObjectType):
    total_usd       = Float()
    timestamp       = DateTime()

class ValueHistory(ObjectType):
    user            = Field(User)
    portfolio_value = List(ValueHistoryEntry)

class PredictionHistoryEntry(ObjectType):
    usd             = Float()
    prediction      = Float()
    timestamp       = DateTime()

class PredictionHistory(ObjectType):
    user                = Field(CoinGecko)
    bitcoin_predictions = List(PredictionHistoryEntry)

    

