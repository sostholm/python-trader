import graphene
from graphene import String
from graphene.relay import Node
import os
from exchanges import gateio
import exchanges
# from models import User as UserNode
# from models import Position as PositionNode
# from models import Order as OrderNode
# from models import User
from models import *
from exchanges import AddBittrexOrder
# from mutations import AddUser, AddPosition, AddOrder
from starlette.authentication import requires
import mutations
from bson import ObjectId
from exchanges import Bittrex, Cdc, GateIO, Ethereum, Binance, Balance
# from mutations import AddCoinGecko
import time
from web_push import send_web_push
# api_key = os.environ['api_key']
# secret  = os.environ['secret']

# client = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb://root:{os.environ["PASSWORD"]}@pine64:27017')

class Query(graphene.ObjectType):
    # node = Node.Field()
    # user = graphene.Field(UserNode, id=graphene.String())
    # order       = graphene.Field(Order1, args={'id': graphene.String(), 'symbol': graphene.String()})
    # exchange    = graphene.Field(Exchange, args={'id': graphene.String(), 'name': graphene.String()})
    my_balance  = graphene.List(Balance, args={'id': graphene.String()})
    accounts    = graphene.List(AccountNode, args={'id': graphene.String()})
    wallets     = graphene.List(WalletNode, args={'id': graphene.String()})
    exchanges   = graphene.List(ExchangeNode)
    wallet_types= graphene.List(WalletTypeNode)
    bittrex     = graphene.Field(Bittrex)
    crypto_cdc  = graphene.Field(Cdc)
    gateio      = graphene.Field(GateIO)
    ethereum    = graphene.Field(Ethereum)
    coin_gecko  = graphene.Field(CoinGeckoNode)
    binance     = graphene.Field(Binance)
    notify      = graphene.Field(graphene.String, args={'id': graphene.String(), 'text': graphene.String()})
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
    def resolve_my_balance(self, info, id=''):
        if id == '':
            id = info.context['user'].id
        user = User.objects(id=ObjectId(id)).first()
        return user.portfolio

    def resolve_exchanges(self, info):
    	return list(Exchange.objects.all())

    def resolve_wallet_types(self, info):
    	return list(WalletType.objects.all())

    def resolve_accounts(self, info, id=''):
        if id == '':
            id = info.context['user'].id
        user = User.objects(id=ObjectId(id)).first()
        return user.accounts

    def resolve_wallets(self, info, id=''):
        if id == '':
            id = info.context['user'].id
        user = User.objects(id=ObjectId(id)).first()
        return user.wallets

    def resolve_bittrex(self, info):
        return Bittrex()

    def resolve_crypto_cdc(self, info):
        return Cdc()

    def resolve_gateio(self, info):
        return GateIO()
    
    def resolve_ethereum(self, info):
        return Ethereum()

    def resolve_coin_gecko(self, info):
        coin_gecko = CoinGecko.objects().first()
        return coin_gecko

    def resolve_binance(self, info):
        return Binance()

    def resolve_notify(self, info, id, text):
        user = User.objects(id=ObjectId(id)).first()
        if user.subscription:
            send_web_push(user.subscription, text)
            return 'Success'
        else:
            return 'No subscription'


class Mutation(graphene.ObjectType):

    # add_user        = mutations.AddUser.Field()
    add_exchange    = mutations.AddExchange.Field()
    add_wallet_type = mutations.AddWalletType.Field()
    add_account     = mutations.AddAccount.Field()
    add_wallet      = mutations.AddWallet.Field()
    add_token       = mutations.AddToken.Field()
    update_exchange = mutations.UpdateExchange.Field()
    # update_user     = mutations.UpdateUser.Field()
    add_subscription= mutations.AddSubscription.Field()
    add_exchange_subscription = mutations.AddSubscription.Field()
    add_bittrex_order = AddBittrexOrder.Field()
    # add_coin_gecko    = AddCoinGecko.Field()
    update_coin_gecko = mutations.UpdateCoinGecko.Field()
    # remove_exchange_subscription = mutations.RemoveSubscription.Field()
        # add_position    = AddPosition.Field()
        # add_order       = AddOrder.Field()

class TimerMiddleware:
    def resolve(self, next, root, info, **args):
        start = time.time()
        result = next(root, info, **args)
        print(f'request {time.time() - start}s')
        return result

# class DBMiddleware:
#     async def resolve(self, next, root, info, **args):
#         start = time.time()
#         coin_gecko = await db.coin_gecko.find_one()
#         info.context['coin_gecko'] = coin_gecko
#         print(f'request {time.time() - start}s')
#         return next(root, info, **args)

schema = graphene.Schema(query=Query, mutation=Mutation)
#, mutation=Mutation

# query = """
# query {
#     order(id: "664789", symbol: "CROBTC") {
#         id
#         created_at
#     }
# }
# """

# print(schema.execute(query).data['order'])