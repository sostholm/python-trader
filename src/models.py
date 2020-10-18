from asyncio import events
from os import name
import graphene
from graphene       import String
from graphene.relay import Node
from graphene_mongo import MongoengineConnectionField, MongoengineObjectType
from datetime       import datetime
from mongoengine    import Document, EmbeddedDocument, connect
from mongoengine    import (DateTimeField, FloatField, StringField, IntField,
ReferenceField, ListField, EmbeddedDocumentListField, DictField, BinaryField)

import aiohttp
import json
import os


COIN_GECKO = 'https://api.coingecko.com/api/v3'

PASSWORD = None

if 'PASSWORD' in os.environ:
    PASSWORD = os.environ["PASSWORD"]
else:
    with open('/run/secrets/db_password', 'r') as file:
        PASSWORD = file.read().replace('\n', '')


connect('trader', host=f'mongodb://pine64:27017', username='root', password=PASSWORD, authentication_source='admin')

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(fetch) as resp:
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

class Position(EmbeddedDocument):
    # currency_pair   = ReferenceField('CurrencyPair')
    held_currency   = StringField()
    amount          = FloatField()
    date            = DateTimeField()
    type            = StringField()
    full_info       = DictField()

class Exchange(Document):
    meta            = {'collection': 'exchanges'}
    name            = StringField()

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

class CoinGecko(Document):
    last_price_update   = DateTimeField()
    # current_prices      = DictField(default={})
    coin_list           = ListField(DictField())
    subscriptions       = ListField(StringField(), default=[])
    loop_state          = StringField(default="stopped", choices=["start", "running", "stop","stopped"])

class Account(EmbeddedDocument):
    meta            = {'collection': 'accounts'}
    api_key         = StringField(required=True)
    secret          = StringField(required=True)
    exchange        = ReferenceField(Exchange, required=True)
    subscriptions   = ListField(StringField())
    positions       = EmbeddedDocumentListField(Position)
    position_history= EmbeddedDocumentListField(Position)

class WalletType(Document):
    meta = {'collection': 'wallet_types'}
    name = StringField()

class Wallet(EmbeddedDocument):
    meta            = {'collection': 'wallets'}
    name            = StringField()
    address         = StringField()
    wallet_type     = ReferenceField(WalletType)
    tokens          = ListField(StringField())

class TotalValue(EmbeddedDocument):
    timestamp       = DateTimeField(required=True, default=lambda: datetime.now())
    usd_value       = IntField()

class User(Document):
    meta            = {'collection': 'users'}
    username        = StringField(required=True)
    password        = StringField(required=True)
    last_update     = DateTimeField()
    portfolio       = ListField(default=[])
    total_value     = EmbeddedDocumentListField(TotalValue)
    subscription    = DictField()
    loop_state      = StringField(default="stopped", choices=["start", "running", "stop","stopped"])
    accounts        = EmbeddedDocumentListField(Account)
    wallets         = EmbeddedDocumentListField(Wallet)
    events          = ListField(default=[])

class UserN(MongoengineObjectType):
    class Meta:
        model = User
        interfaces = (Node,)

class AccountNode(MongoengineObjectType):
    class Meta:
        model = Account
        interfaces = (Node,)

class ExchangeNode(MongoengineObjectType):
    class Meta:
        model = Exchange

    instruments         = graphene.JSONString()
    exchange_tickers    = graphene.JSONString()
    coins               = graphene.JSONString()
    coin_ticker         = graphene.JSONString()

    async def resolve_exchange_tickers(self, info):
        return fetch(f'https://api.coingecko.com/api/v3/exchanges/{self.name.lower()}/tickers')

    async def resolve_instruments(self, info):
        if self.instruments_url:
            return fetch(self.instruments_url)

class WalletNode(MongoengineObjectType):
    class Meta:
        model = Wallet
        interfaces = (Node,) 

class WalletTypeNode(MongoengineObjectType):
    class Meta:
        model = WalletType

# class PositionNode(MongoengineObjectType):
#     class Meta:
#         model = Position
#         interfaces = (Node,)

# class OrderNode(graphene.ObjectType):
#     class Meta:
#         model = Order1
#         interfaces = (Node,)

class CoinGeckoNode(MongoengineObjectType):
    class Meta:
        model = CoinGecko
        interfaces = (Node,)

    

