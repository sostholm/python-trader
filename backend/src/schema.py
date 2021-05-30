import graphene
from graphene import String
from graphene.relay import Node
import os
from exchanges import gateio
import exchanges
from models import Exchange, WalletType, User, CoinGecko, CoinGeckoCoin, ValueHistory, PredictionHistory
from exchanges import AddBittrexOrder
from starlette.authentication import requires
import mutations
from bson import ObjectId
from exchanges import Bittrex, Cdc, GateIO, Ethereum, Cardano, Binance, Balance
import time
from web_push import send_web_push
from requested_fields import get_projection
from guard import guard
# api_key = os.environ['api_key']
# secret  = os.environ['secret']

# client = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb://root:{os.environ["PASSWORD"]}@pine64:27017')

def get_user_projection_and_mongo(info):
    if 'request' in info.context:
        id = info.context['request'].user.display_name
    else:
        id = info.context['user']['_id']
    fields = get_projection(info, True)

    if 'request' in info.context:
        client = info.context['request'].app.mongo
    else:
        client = info.context['client']

    return id, fields, client

class Query(graphene.ObjectType):
    exchanges   = graphene.List(Exchange)
    wallet_types= graphene.List(WalletType)
    me          = graphene.Field(User)
    bittrex     = graphene.Field(Bittrex)
    crypto_cdc  = graphene.Field(Cdc)
    gateio      = graphene.Field(GateIO)
    ethereum    = graphene.Field(Ethereum)
    cardano     = graphene.Field(Cardano)
    coin_gecko  = graphene.Field(CoinGecko)
    binance     = graphene.Field(Binance)
    notify      = graphene.Field(graphene.String, args={'id': graphene.String(), 'text': graphene.String()})
    value_history       = graphene.Field(ValueHistory)
    prediction_history   = graphene.Field(PredictionHistory)

    @guard
    async def resolve_me(self, info):
        id, fields, client = get_user_projection_and_mongo(info)
        user = await client.trader.users.find_one({'_id': ObjectId(id)}, fields)
        return user

    @guard
    async def resolve_value_history(self, info):
        id, fields, client = get_user_projection_and_mongo(info)
        user = await client.trader.value_history.find_one({'user': ObjectId(id)}, fields)
        return user

    @guard
    async def resolve_prediction_history(self, info):
        id, fields, client = get_user_projection_and_mongo(info)
        user = await client.trader.value_history.find_one({'user': ObjectId('5f526ffee5da7706984ba8ca')}, fields)
        return user

    @guard
    async def resolve_exchanges(self, info):
        fields = get_projection(info, True)
        result = []
        async for document in info.context['request'].app.mongo.trader.exchanges.find({}, fields):
            result.append(document)
        return result

    @guard
    async def resolve_wallet_types(self, info):
        fields = get_projection(info, True)
        result = []
        async for document in info.context['request'].app.mongo.trader.wallet_types.find({}, fields):
            result.append(document)
        return result

    @guard
    def resolve_bittrex(self, info):
        return Bittrex()

    @guard
    def resolve_crypto_cdc(self, info):
        return Cdc()

    @guard
    def resolve_gateio(self, info):
        return GateIO()

    @guard
    def resolve_ethereum(self, info):
        return Ethereum()

    @guard
    def resolve_cardano(self, info):
        return Cardano()

    @guard
    def resolve_binance(self, info):
        return Binance()

    @guard
    async def resolve_coin_gecko(self, info):
        fields = get_projection(info, True)
        coin_gecko = await info.context['request'].app.mongo.trader.coin_gecko.find_one({}, fields)
        return coin_gecko

    @guard
    async def resolve_notify(self, info, id, text):
        if id == '':
            id = info.context['user'].id
        fields = get_projection(info, True)
        user = await info.context['request'].app.mongo.trader.users.find_one({'_id': ObjectId(id)}, fields)
        if user['subscription']:
            send_web_push(user['subscription'], text)
            return 'Success'
        else:
            return 'No subscription'


class Mutation(graphene.ObjectType):
    add_account     = mutations.AddAccount.Field()
    add_wallet      = mutations.AddWallet.Field()
    add_token       = mutations.AddToken.Field()
    add_subscription= mutations.AddSubscription.Field()
    update_token    = mutations.UpdateToken.Field()
    login           = mutations.Login.Field()


class TimerMiddleware:
    def resolve(self, next, root, info, **args):
        start = time.time()
        result = next(root, info, **args)
        print(f'request {time.time() - start}s')
        return result


schema = graphene.Schema(query=Query, mutation=Mutation)
