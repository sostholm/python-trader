import graphene
from graphene import String
from graphene.relay import Node
from graphene_mongo import MongoengineConnectionField, MongoengineObjectType
import os
# from models import User as UserNode
# from models import Position as PositionNode
# from models import Order as OrderNode
# from models import User
from models import ExchangeNode, Exchange, Order

# from mutations import AddUser, AddPosition, AddOrder

from crypto_dot_com_api import CryptoAPI
import mutations
from bson import ObjectId

api_key = os.environ['api_key']
secret  = os.environ['secret']

api = CryptoAPI(key=api_key, sec=secret)

class Query(graphene.ObjectType):
    # node = Node.Field()
    # user = graphene.Field(UserNode, id=graphene.String())
    order = graphene.Field(Order, args={'id': graphene.String(), 'symbol': graphene.String()})
    exchange = graphene.Field(ExchangeNode, args={'id': graphene.String(), 'name': graphene.String()})
    # orders = graphene.List(Order)
    # all_microbes = MongoengineConnectionField(Microbe)
    # all_Probiotics = MongoengineConnectionField(Probiotic)
    # search = graphene.List(SearchResult, q=graphene.String())

    # def resolve_search(self, info, **args):
    #     q = args.get("q")
    #     microbes = MicrobeModel.objects(species__contains=q).all()
    #     return microbes
    # def resolve_user(self, info, **args):
    #     user_id  = args.get('id')
    #     user = User.objects(id=user_id).first()
    #     return user
    def resolve_exchange(self, info, id, name=""):
        exchange = Exchange.objects(id=ObjectId(id)).first()
        return exchange

    def resolve_order(self, info, symbol, id):
        order = api.get_order(sym=symbol, oid=id)
        if order['code'] != '0':
            raise Exception()
        return order['data']['order_info']


class Mutation(graphene.ObjectType):

    add_user        = mutations.AddUser.Field()
    add_exchange    = mutations.AddExchange.Field()
    update_exchange = mutations.UpdateExchange.Field()
    add_exchange_subscription = mutations.AddSubscription.Field()
    # remove_exchange_subscription = mutations.RemoveSubscription.Field()
        # add_position    = AddPosition.Field()
        # add_order       = AddOrder.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

# query = """
# query {
#     order(id: "664789", symbol: "CROBTC") {
#         id
#         created_at
#     }
# }
# """

# print(schema.execute(query).data['order'])