import graphene
from graphene   import Mutation, String, Field
from models     import User, Position, Exchange, Account, CoinGecko, Wallet, WalletType, fetch
from exchanges  import Order
from encrypt    import password_encrypt, password_decrypt
from bson       import ObjectId
from datetime   import datetime, timedelta
from guard      import guard
from util       import make_wallets, make_exchanges
import json
import bcrypt
import asyncio
import jwt
import os



class AddUser(graphene.Mutation):

    class Input:
        username    = graphene.String(required=True)
        password    = graphene.String(required=True)
    user = graphene.Field(User)

    @guard
    async def mutate(root, info, **input):
        user = dict(
            username    = input['username'],
            password    = bcrypt.hashpw(input['password'].encode(), bcrypt.gensalt(12)).decode('utf-8'),
        )
        await info.context['request'].app.mongo.trader.users.insert_one(user)
        return AddUser(user=user)

class AddCoinGecko(graphene.Mutation):
    coin_gecko = graphene.Field(CoinGecko)
    
    @guard
    def mutate(root, info, **input):
        cg = CoinGecko()
        cg.save()
        return AddCoinGecko(coin_gecko=cg)

class AddAccount(graphene.Mutation):
    class Input:
        exchange_name   = graphene.String(required=True)
        api_key         = graphene.String(required=True)
        secret          = graphene.String(required=True)
        password        = graphene.String(required=True)

    account = graphene.Field(Account)

    @guard
    async def mutate(root, info, **input):
        id = info.context['request'].user.display_name
        exchange = await info.context['request'].app.mongo.trader.exchanges.find_one({'name': input['exchange_name']})
        account =  dict(
            exchange    = exchange['_id'],
            api_key     = password_encrypt(message=input['api_key'].encode('utf-8'), password=input['password']).decode('utf-8'),
            secret      = password_encrypt(message=input['secret'].encode('utf-8'), password=input['password']).decode('utf-8')
        )
        await info.context['request'].app.mongo.trader.users.update_one({'_id': ObjectId(id)}, {'$push': {'accounts': account}})
        return AddAccount(account=account)

class AddWallet(graphene.Mutation):
    class Input:
        name            = graphene.String(required=True)
        address         = graphene.String(required=True)
        wallet_type     = graphene.String(required=True)

    wallet = graphene.Field(Wallet)

    @guard
    async def mutate(root, info, **input):
        id = info.context['request'].user.display_name
        
        wallet_type = await info.context['client'].trader.wallet_types.find_one({'name': input['wallet_type']})
        wallet = dict(
            name        = input['name'],
            address     = input['address'],
            wallet_type = ObjectId(wallet_type['_id'])
        )
        
        await info.context['request'].app.mongo.trader.users.update_one({'_id': ObjectId(id)}, {'$push': {'wallet': wallet}})
        return AddWallet(wallet=wallet)

class AddToken(graphene.Mutation):
    class Input:
        wallet_name     = graphene.String(required=True)
        token           = graphene.String(required=True)

    token = graphene.Field(graphene.String)

    @guard
    async def mutate(root, info, **input):
        id = info.context['request'].user.display_name
        
        await info.context['request'].app.mongo.trader.users.update_one({'_id': ObjectId(id), 'wallets.name': input['wallet_name']}, {'$push': {'wallets.$.tokens': input['token']}})
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

    @guard
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

    @guard
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

class UpdateToken(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)

    token = graphene.Field(graphene.String)

    @guard
    async def mutate(root, info, **input):
        token_id = jwt.decode(input['token'], 'secret', algorithms=['HS256'])['id']
        id = info.context['request'].user.display_name
        assert token_id == id

        token = jwt.encode({'exp': datetime.utcnow() + timedelta(seconds=1800), 'id': id}, 'secret', algorithm='HS256')

        return UpdateToken(token=token)

class Login(Mutation):
    class Arguments:
        username = String(required=True)
        password = String(required=True)

    token = Field(String)

    async def mutate(root, info, **input):
        client  = info.context['request'].app.mongo
        request = info.context['request']
        
        user = await client.trader.users.find_one({'username': input['username']})
        exchanges = await client.trader.exchanges.find({}).to_list(length=100)
        wallet_types = await client.trader.wallet_types.find({}).to_list(length=100)

        if not user:
            raise Exception('User not found')
        
        if not bcrypt.checkpw(input['password'].encode(), user['password'].encode()):
            raise Exception('Wrong Username/Password')

        user['password_decrypted'] = input['password']
        
        user['exchanges'] = make_exchanges(user, input['password'], exchanges)
        user['wallets'] = make_wallets(user, wallet_types)

        if user['loop_state'] != 'running':
            try:
                payload = {'_id': str(user['_id']), 'wallets': user['wallets'], 'exchanges': user['exchanges']}
                await fetch(request.app.aiohttp_session, f'http://{os.environ["WORKER"]}:8002', 'post', body={"user": payload})
            except Exception as e:
                print(e)

        token = jwt.encode({'exp': datetime.utcnow() + timedelta(seconds=1800), 'id': str(user['_id']), 'access': 'write'}, 'secret', algorithm='HS256')
        return Login(token=token)


class AddSubscription(graphene.Mutation):
    class Arguments:
        endpoint            = graphene.String()
        expirationTime      = graphene.String()
        p256dh              = graphene.String()
        auth                = graphene.String()

    stuff = graphene.Field(graphene.String)

    
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

#     
#     def mutate(root, info, **input):
#         exchange = Exchange.objects(id=ObjectId(input['_id'])).first()
#         exchange.subscriptions.append(input['channel'])
#         exchange.save()
#         return AddSubscription(exchange=exchange)