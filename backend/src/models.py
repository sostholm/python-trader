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
    get_secret('db_password').replace('\n', '')
    # with open('/run/secrets/db_password', 'r') as file:
    #     PASSWORD = file.read().replace('\n', '')


connect('trader', host=f'mongodb://pine64:27017', username='root', password=PASSWORD, authentication_source='admin')
client = motor.motor_asyncio.AsyncIOMotorClient()

async def fetch(url, type='get', body={}):
    async with aiohttp.ClientSession() as session:
        if type == 'get':
            async with session.get(fetch) as resp:
                print(resp.status)
                resp = await resp.text()
                return json.loads(resp)

        if type == 'post':
            async with session.post(url, json=body) as resp:
                print(resp.status)
                resp = await resp.text()
                return json.loads(resp)
        

# class Order(graphene.ObjectType):
#     side        = StringField()
#     fee         = FloatField()
#     created_at  = DateTimeField()
#     deal_price  = FloatField()
#     avg_price   = FloatField()
#     volume      = FloatField()
#     price       = FloatField()
#     status_msg  = StringField()
#     remain_volume = FloatField()
#     baseCoin    = StringField()
#     countCoin   = StringField()
#     status      = IntField()
#     all_details = DictField()

# class Order1(graphene.ObjectType):
#     side        = graphene.String()
#     fee         = graphene.Float()
#     created_at  = graphene.DateTime()
#     deal_price  = graphene.Float()
#     avg_price   = graphene.Float()
#     volume      = graphene.Float()
#     price       = graphene.Float()
#     status_msg  = graphene.String()
#     remain_volume = graphene.Float()
#     baseCoin    = graphene.String()
#     countCoin   = graphene.String()
#     status      = graphene.Int()
#     all_details = graphene.JSONString()

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

# class CoinGeckoCoin(Document):
#     id                              = StringField(),
#     symbol                          = StringField(),
#     name                            = StringField(),
#     image                           = StringField(),
#     current_price                   = FloatField(),
#     market_cap                      = FloatField(),
#     market_cap_rank                 = IntField(),
#     fully_diluted_valuation         = IntField(),
#     total_volume                    = IntField(),
#     high_24h                        = FloatField(),
#     low_24h                         = FloatField(),
#     price_change_24h                = FloatField(),
#     price_change_percentage_24h     = FloatField(),
#     market_cap_change_24h           = IntField(),
#     market_cap_change_percentage_24h= FloatField(),
#     circulating_supply              = IntField(),
#     total_supply                    = IntField(),
#     max_supply                      = IntField(),
#     ath                             = FloatField(),
#     ath_change_percentage           = FloatField(),
#     ath_date                        = DateTimeField(),
#     atl                             = FloatField(),
#     atl_change_percentage           = FloatField(),
#     atl_date                        = DateTimeField(),
#     roi                             = DictField(default={}),
#     last_updated                    = DateTimeField()
#     price_change_percentage_14d_in_currency     = FloatField(),
#     price_change_percentage_1h_in_currency      = FloatField(),
#     price_change_percentage_24h_in_currency     = FloatField(),
#     price_change_percentage_30d_in_currency     = FloatField(),
#     price_change_percentage_7d_in_currency      = FloatField()
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
    # meta = {'collection': 'wallet_types'}
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
    currency                            = String()
    total                               = Float()
    available                           = Float()
    usd                                 = Float()
    priceChangePercentage1hInCurrency   = Float()
    priceChangePercentage24hInCurrency  = Float()
    exchange                            = String()

class User(ObjectType):
    # meta            = {'collection': 'users'}
    username        = String()
    password        = String()
    last_update     = Int()
    portfolio       = List(UserBalance)
    subscription    = JSONString()
    loop_state      = String()
    accounts        = List(Account)
    wallets         = List(Wallet)
    events          = List(Event)

# class TotalValue(ObjectType):
#     timestamp       = DateTime()
#     usd_value       = Int()

# class ValueHistory(ObjectType):
#     # meta            = {'collection': 'value_history'}
#     user            = String()
#     total_value     = List(Field(TotalValue))

# class UserN(MongoengineObjectType):
#     class Meta:
#         model = User
#         interfaces = (Node,)

# class AccountNode(MongoengineObjectType):
#     class Meta:
#         model = Account
#         interfaces = (Node,)

# class ExchangeNode(MongoengineObjectType):
#     class Meta:
#         model = Exchange

#     instruments         = graphene.JSONString()
#     exchange_tickers    = graphene.JSONString()
#     coins               = graphene.JSONString()
#     coin_ticker         = graphene.JSONString()

#     async def resolve_exchange_tickers(self, info):
#         return fetch(f'https://api.coingecko.com/api/v3/exchanges/{self.name.lower()}/tickers')

#     async def resolve_instruments(self, info):
#         if self.instruments_url:
#             return fetch(self.instruments_url)

# class WalletNode(MongoengineObjectType):
#     class Meta:
#         model = Wallet
#         interfaces = (Node,) 

# class WalletTypeNode(MongoengineObjectType):
#     class Meta:
#         model = WalletType

# class PositionNode(MongoengineObjectType):
#     class Meta:
#         model = Position
#         interfaces = (Node,)

# class OrderNode(graphene.ObjectType):
#     class Meta:
#         model = Order1
#         interfaces = (Node,)

# class CoinGeckoNode(MongoengineObjectType):
#     class Meta:
#         model = CoinGecko
#         interfaces = (Node,)

    

