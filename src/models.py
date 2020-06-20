import graphene
from graphene       import String
from graphene.relay import Node
from graphene_mongo import MongoengineConnectionField, MongoengineObjectType
from datetime       import datetime
from mongoengine    import Document, EmbeddedDocument
from mongoengine    import (DateTimeField, FloatField, StringField, IntField,
ReferenceField, ListField, EmbeddedDocumentListField, DictField)


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
    currency_pair   = StringField()
    held_currency   = StringField()
    amount          = FloatField()
    date            = DateTimeField()
    full_info       = DictField()

class Market(graphene.ObjectType):
    pass

class User(Document):
    meta        = {'collection': 'users'}
    username    = StringField(required=True)
    password    = StringField(required=True)
    api_key     = StringField(required=False)
    secret      = StringField(required=False)
    balance     = graphene.List(Position)
    position_history = EmbeddedDocumentListField(Position)
    orders      = graphene.List(Order)
    order_history    = graphene.List(Order)


class UserNode(MongoengineObjectType):
    class Meta:
        model = User
        interfaces = (Node,)


class PositionNode(MongoengineObjectType):
    class Meta:
        model = Position
        interfaces = (Node,)


# class OrderNode(MongoengineObjectType):
#     class Meta:
#         model = Order
#         interfaces = (Node,)