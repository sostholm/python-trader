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


class Position(EmbeddedDocument):
    currency_pair   = ReferenceField('CurrencyPair')
    held_currency   = StringField()
    amount          = FloatField()
    date            = DateTimeField()
    full_info       = DictField()

class Trade(EmbeddedDocument):
    quantity        = FloatField()
    trade_type      = StringField()
    price           = FloatField()
    timestamp       = DateTimeField()

class CurrencyPair(Document):
    meta            = {'collection': 'currency_pairs'}
    trades = EmbeddedDocumentListField(Trade)
    pair = StringField()


class Exchange(Document):
    meta            = {'collection': 'exchanges'}
    name            = StringField()
    exchange_api    = StringField()
    instruments_url = StringField()
    currency_pairs  = ListField(ReferenceField(CurrencyPair))
    loop_state      = StringField(default="stopped", choices=["running","halting","stopped"])
    subscriptions   = ListField(StringField())

class User(Document):
    meta            = {'collection': 'users'}
    username        = StringField(required=True)
    password        = StringField(required=True)
    api_key         = StringField(required=False)
    secret          = StringField(required=False)
    loop_state      = StringField(default="stopped", choices=["running","halting","stopped"])
    subscriptions   = DictField()
    balance         = graphene.List(Position)
    position_history= EmbeddedDocumentListField(Position)
    orders          = graphene.List(Order)
    order_history   = graphene.List(Order)


class UserNode(MongoengineObjectType):
    class Meta:
        model = User
        interfaces = (Node,)

class ExchangeNode(MongoengineObjectType):
    class Meta:
        model = Exchange
        interfaces = (Node,)

    instruments = graphene.JSONString()

    async def resolve_instruments(self, info):
        if self.instruments_url:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.instruments_url) as resp:
                    print(resp.status)
                    resp = await resp.text()
                    print(resp)
                    return json.loads(resp)
        

class PositionNode(MongoengineObjectType):
    class Meta:
        model = Position
        interfaces = (Node,)

class OrderNode(graphene.ObjectType):
    class Meta:
        model = Order
        interfaces = (Node,)