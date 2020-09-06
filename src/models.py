from os import name
import graphene
from graphene       import String
from graphene.relay import Node
from graphene_mongo import MongoengineConnectionField, MongoengineObjectType
from datetime       import datetime
from mongoengine    import Document, EmbeddedDocument
from mongoengine    import (DateTimeField, FloatField, StringField, IntField,
ReferenceField, ListField, EmbeddedDocumentListField, DictField, BinaryField)

import aiohttp
import json

from coin_gecko_api import get_timestamp

COIN_GECKO = 'https://api.coingecko.com/api/v3'

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
    exchange_api    = StringField()
    loop_state      = StringField(default="stopped", choices=["start", "running", "stop","stopped"])
    subscriptions   = ListField(StringField())

class CoinGecko(Document):
    current_prices  = DictField(default={})
    coin_list       = DictField(default={})
    subscriptions   = ListField(StringField(), default=[])
    loop_state      = StringField(default="stopped", choices=["start", "running", "stop","stopped"])

class Account(EmbeddedDocument):
    meta            = {'collection': 'accounts'}
    api_key         = StringField(required=True)
    secret          = StringField(required=True)
    loop_state      = StringField(default="stopped", choices=["start", "running", "stop","stopped"])
    exchange        = ReferenceField(Exchange, required=True)
    subscriptions   = ListField(StringField())
    positions       = EmbeddedDocumentListField(Position)
    position_history= EmbeddedDocumentListField(Position)

class Wallet(EmbeddedDocument):
    meta            = {'collection': 'wallets'}
    address         = StringField()
    wallet_type     = StringField()
    tokens          = DictField()

class TotalValue(EmbeddedDocument):
    timestamp       = DateTimeField(required=True, default=lambda: datetime.now())
    usd_value       = IntField()

class User(Document):
    meta            = {'collection': 'users'}
    username        = StringField(required=True)
    password        = StringField(required=True)
    portfolio       = DictField()
    total_value     = EmbeddedDocumentListField(TotalValue)
    subscription    = StringField()
    accounts        = EmbeddedDocumentListField(Account)
    wallets         = EmbeddedDocumentListField(Wallet)

class UserNode(MongoengineObjectType):
    class Meta:
        model = User
        interfaces = (Node,)

class AccountNode(MongoengineObjectType):
    class Meta:
        model = Exchange
        interfaces = (Node,)

class ExchangeNode(MongoengineObjectType):
    class Meta:
        model = Exchange
        interfaces = (Node,)

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

    

