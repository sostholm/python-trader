from os import name
import graphene
# UserN, ExchangeNode, AccountNode, WalletNode, WalletTypeNode
from models import User, Position, Exchange, Account, CoinGecko, Wallet, WalletType
from exchanges import Order
from encrypt import password_encrypt, password_decrypt
import json
import bcrypt
from bson import ObjectId
import asyncio


class AddUser(graphene.Mutation):

    class Input:
        username    = graphene.String(required=True)
        password    = graphene.String(required=True)
    user = graphene.Field(User)

    @staticmethod
    async def mutate(root, info, **input):
        user = dict(
            username    = input['username'],
            password    = bcrypt.hashpw(input['password'].encode(), bcrypt.gensalt(12)).decode('utf-8'),
        )
        await info.context['client'].trader.users.insert_one(user)
        return AddUser(user=user)

class AddCoinGecko(graphene.Mutation):
    
    coin_gecko = graphene.Field(CoinGecko)
    @staticmethod
    def mutate(root, info, **input):
        cg = CoinGecko()
        cg.save()
        return AddCoinGecko(coin_gecko=cg)

class AddAccount(graphene.Mutation):
    class Input:
        exchange_id     = graphene.String(required=True)
        api_key         = graphene.String(required=True)
        secret          = graphene.String(required=True)
        password        = graphene.String(required=True)

    account = graphene.Field(Account)

    @staticmethod
    async def mutate(root, info, **input):
        id = info.context['request'].user.display_name
        exchange = await info.context['client'].trader.exchanges.find_one({'_id': input['exchange_id']})
        account =  dict(
            exchange    = exchange['_id'],
            api_key     = password_encrypt(message=input['api_key'].encode('utf-8'), password=input['password']).decode('utf-8'),
            secret      = password_encrypt(message=input['secret'].encode('utf-8'), password=input['password']).decode('utf-8')
        )
        await info.context['client'].trader.users.update_one({'_id': ObjectId(id)}, {'$push': {'account': account}})
        return AddAccount(account=account)

class AddWallet(graphene.Mutation):
    class Input:
        name            = graphene.String(required=True)
        address         = graphene.String(required=True)
        wallet_type     = graphene.String(required=True)

    wallet = graphene.Field(Wallet)

    @staticmethod
    async def mutate(root, info, **input):
        id = info.context['request'].user.display_name
        
        wallet_type = await info.context['client'].trader.wallet_types.find_one({'_id': input['wallet_type']})
        wallet = dict(
            name        = input['name'],
            address     = input['address'],
            wallet_type = ObjectId(wallet_type['_id'])
        )
        
        await info.context['client'].trader.users.update_one({'_id': ObjectId(id)}, {'$push': {'wallet': wallet}})
        return AddWallet(wallet=wallet)

class AddToken(graphene.Mutation):
    class Input:
        wallet_name     = graphene.String(required=True)
        token           = graphene.String(required=True)

    token = graphene.Field(graphene.String)

    @staticmethod
    async def mutate(root, info, **input):
        id = info.context['request'].user.display_name
        
        await info.context['client'].trader.users.update_one({'_id': ObjectId(id), 'wallets.name': input['wallet_name']}, {'$push': {'tokens': input['token']}})
        return AddToken(token=input['token'])

class AddPosition(graphene.Mutation):
    class Arguments:
        user_id         = graphene.String(required=True)
        currency_pair   = graphene.String(required=True)
        held_currency   = graphene.String(required=True)
        amount          = graphene.Float(required=True)
        date            = graphene.types.datetime.DateTime()
        full_info       = graphene.types.json.JSONString()
        type            = graphene.String(required=True)

    position = graphene.Field(Position)

    @staticmethod
    def mutate(root, info, **input):
        pb = Position(
                currency_pair   = input['currency_pair'],
                held_currency   = input['held_currency'],
                amount          = input['amount'],
                date            = input['date'],
                full_info       = input['full_info'],
                type            = input['type']
            )
        user = User.objects(id=input['user_id']).first()
        user.balance.append(pb).save()

        return AddPosition(position=pb)

class AddOrder(graphene.Mutation):
    class Arguments:
        exchange    = graphene.String(required=True)
        market      = graphene.String(required=True)
        direction   = graphene.String(required=True)
        order_type  = graphene.String(required=True)
        quantity    = graphene.Float(required=True)
        limit       = graphene.Float(required=True)

    order = graphene.Field(Order)

    @staticmethod
    async def mutate(root, info, **input):
        id = info.context['request'].user.display_name
        exchange = await info.context['client'].trader.exchanges.find_one({'_id': input['exchange_id']})
        order = dict(
            exchange    = exchange['_id'],
            market      = input['market'],
            direction   = input['direction'],
            order_type  = input['order_type'],
            quantity    = input['quantity'],
            limit       = input['limit'],
        )
        await info.context['client'].trader.users.update_one({'_id': ObjectId(id)}, {'$push': {'order': order}})

        return AddOrder(order=order)

# class AddExchange(graphene.Mutation):
#     class Arguments:
#         name = graphene.String()

#     exchange = graphene.Field(Exchange)

#     @staticmethod
#     async def mutate(root, info, **input):
#         await info.context['client'].trader.users.insert_one({'name': input['name']})

#         return AddExchange(exchange={'name': input['name']})

# class AddWalletType(graphene.Mutation):
#     class Arguments:
#         name = graphene.String()

#     wallet_type = graphene.Field(WalletTypeNode)

#     @staticmethod
#     def mutate(root, info, **input):
#         obj = WalletType(
#             name = input['name'],
#         )
#         obj.save()

#         return AddWalletType(wallet_type=obj)
        
# class UpdateUser(graphene.Mutation):
#     class Arguments:
#         user_id     = graphene.String()
#         password    = graphene.String()
#         subscription= graphene.String()
#         loop_state  = graphene.String()

#     user = graphene.Field(User)

#     @staticmethod
#     def mutate(root, info, **input):
#         id = info.context['request'].user.display_name

#         if 'password' in input:
#             user.password   = bcrypt.hashpw(input['password'], bcrypt.gensalt(12)).decode('utf-8')
#         if 'subscription' in input:
#             user.subscription = json.dumps(input['subscription'])
#         if 'loop_state' in input:

#             if input['loop_state'] == 'stop':
#                 user.loop_state = 'stop'

#             else:
#                 raise Exception(f"Exchange loop state is:{user.loop_state}, {input['loop_state']} not allowed")


#         return UpdateUser(user=user)

# class UpdateCoinGecko(graphene.Mutation):
#     class Arguments:
#         loop_state = graphene.String()
    
#     coin_gecko = graphene.Field(CoinGeckoNode)

#     @staticmethod
#     def mutate(root, info, **input):
#         coin_gecko = CoinGecko.objects().first()
#         if 'loop_state' in input:

#             if input['loop_state'] in ['stop', 'stopped']:
#                 coin_gecko.loop_state = input['loop_state']

#             else:
#                 raise Exception(f"Exchange loop state is:{coin_gecko.loop_state}, {input['loop_state']} not allowed")

#             coin_gecko.loop_state = input['loop_state']
#             coin_gecko.save()

#         return UpdateCoinGecko(coin_gecko=coin_gecko)

# class UpdateExchange(graphene.Mutation):
#     class Arguments:
#         _id = graphene.String()
#         name            = graphene.String()
#         exchange_api    = graphene.String()
#         instruments_url = graphene.String()
#         loop_state      = graphene.String()

#     exchange = graphene.Field(ExchangeNode)

#     @staticmethod
#     def mutate(root, info, **input):
#         exchange = Exchange.objects(id=ObjectId(input['_id'])).first()

#         if 'name' in input:
#             exchange.name = input['name']
#         if 'exchange_api' in input:
#             exchange.exchange_api = input['exchange_api']
#         if 'instruments_url' in input:
#             exchange.instruments_url = input['instruments_url']
#         if 'loop_state' in input:

#             if input['loop_state'] in ['stop', 'stopped']:
#                 exchange.loop_state = input['loop_state']

#             else:
#                 raise f"Exchange loop state is:{exchange.loop_state}, {input['loop_state']} not allowed"

#             exchange.loop_state = input['loop_state']

#         exchange.save()
#         return UpdateExchange(exchange=exchange)


class AddSubscription(graphene.Mutation):
    class Arguments:
        endpoint            = graphene.String()
        expirationTime      = graphene.String()
        p256dh              = graphene.String()
        auth                = graphene.String()

    stuff = graphene.Field(graphene.String)

    @staticmethod
    async def mutate(root, info, **input):
        id = info.context['request'].user.display_name

        sub = {"endpoint": input['endpoint'], "expirationTime": None, "keys": {"p256dh": input['p256dh'], "auth": input['auth']}}
        
        await info.context['request'].app.mongo.trader.users.update_one({'_id': ObjectId(id)}, {'$set': {'subscription': sub}})
        return AddSubscription(stuff='worked')

# class RemoveSubscription(graphene.Mutation):
#     class Arguments:
#         _id     = graphene.String()
#         channel = graphene.String()

#     exchange = graphene.Field(ExchangeNode)

#     @staticmethod
#     def mutate(root, info, **input):
#         exchange = Exchange.objects(id=ObjectId(input['_id'])).first()
#         exchange.subscriptions.append(input['channel'])
#         exchange.save()
#         return AddSubscription(exchange=exchange)