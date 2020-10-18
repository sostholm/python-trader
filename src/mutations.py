from os import name
import graphene
from models import UserN, ExchangeNode, User, Position, Exchange, Account, AccountNode, CoinGecko, CoinGeckoNode, Wallet, WalletNode, WalletType, WalletTypeNode
from encrypt import password_encrypt, password_decrypt
import json
import bcrypt
from bson import ObjectId
import asyncio


class AddUser(graphene.Mutation):

    class Input:
        username    = graphene.String(required=True)
        password    = graphene.String(required=True)
    user = graphene.Field(UserN)

    @staticmethod
    def mutate(root, info, **input):
        bl = User(
            username    = input['username'],
            password    = bcrypt.hashpw(input['password'].encode(), bcrypt.gensalt(12)).decode('utf-8'),
        )
        bl.save()
        return AddUser(user=bl)

class AddCoinGecko(graphene.Mutation):
    
    coin_gecko = graphene.Field(CoinGeckoNode)
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

    account = graphene.Field(AccountNode)

    @staticmethod
    def mutate(root, info, **input):
        user = info.context['user']
        user.accounts.append(
            Account(
                exchange    = Exchange.objects(id=ObjectId(input['exchange_id'])).first(),
                api_key     = password_encrypt(message=input['api_key'].encode('utf-8'), password=user.password_decrypted).decode('utf-8'),
                secret      = password_encrypt(message=input['secret'].encode('utf-8'), password=user.password_decrypted).decode('utf-8')
            )
        )
        user.save()
        return AddAccount(account=user.accounts[-1])

class AddWallet(graphene.Mutation):
    class Input:
        name            = graphene.String(required=True)
        address         = graphene.String(required=True)
        wallet_type     = graphene.String(required=True)

    wallet = graphene.Field(WalletNode)

    @staticmethod
    def mutate(root, info, **input):
        user = info.context['user']
        user.wallets.append(
            Wallet(
                name        = input['name'],
                address     = input['address'],
                wallet_type = WalletType.objects(id=ObjectId(input['wallet_type'])).first()
            )
        )
        user.save()
        return AddWallet(wallet=user.wallets[-1])

class AddToken(graphene.Mutation):
    class Input:
        wallet_name     = graphene.String(required=True)
        token           = graphene.String(required=True)

    token = graphene.Field(graphene.String)

    @staticmethod
    def mutate(root, info, **input):
        user = info.context['user']
        wallet = list(filter(lambda wallet: wallet.name == input['wallet_name'] , user.wallets))[0]
        wallet.tokens.append(input['token'])
        user.save()
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

# class AddOrder(graphene.Mutation):
#     class Arguments:
#         user_id     = graphene.String()
#         side        = graphene.String()
#         fee         = graphene.Float()
#         created_at  = graphene.types.datetime.DateTime()
#         deal_price  = graphene.Float()
#         avg_price   = graphene.Float()
#         volume      = graphene.Float()
#         price       = graphene.Float()
#         status_msg  = graphene.String()
#         remain_volume = graphene.Float()
#         baseCoin    = graphene.String()
#         countCoin   = graphene.String()
#         status      = graphene.Int()
#         all_details = graphene.types.json.JSONString()

#     order = graphene.Field(Order)

#     @staticmethod
#     def mutate(root, info, **input):
#         pb = Order(
#             side        = input['side'],
#             fee         = input['fee'],
#             created_at  = input['created_at'],
#             deal_price  = input['deal_price'],
#             avg_price   = input['avg_price'],
#             volume      = input['volume'],
#             price       = input['price'],
#             status_msg  = input['status_msg'],
#             remain_volume = input['remain_volume'],
#             baseCoin    = input['baseCoin'],
#             countCoin   = input['countCoin'],
#             status      = input['status'],
#             all_details = input['all_details'],
#         )
#         user = User.objects(id=input['user_id']).first()
#         user.orders.append(pb).save()

#         return AddOrder(order=pb)

class AddExchange(graphene.Mutation):
    class Arguments:
        name = graphene.String()

    exchange = graphene.Field(ExchangeNode)

    @staticmethod
    def mutate(root, info, **input):
        obj = Exchange(
            name = input['name'],
        )
        obj.save()

        return AddExchange(exchange=obj)

class AddWalletType(graphene.Mutation):
    class Arguments:
        name = graphene.String()

    wallet_type = graphene.Field(WalletTypeNode)

    @staticmethod
    def mutate(root, info, **input):
        obj = WalletType(
            name = input['name'],
        )
        obj.save()

        return AddWalletType(wallet_type=obj)
        
class UpdateUser(graphene.Mutation):
    class Arguments:
        user_id     = graphene.String()
        password    = graphene.String()
        subscription= graphene.String()
        loop_state  = graphene.String()

    user = graphene.Field(User)

    @staticmethod
    def mutate(root, info, **input):
        user = User.objects(id=ObjectId(input['user_id'])).first()

        if 'password' in input:
            user.password   = bcrypt.hashpw(input['password'], bcrypt.gensalt(12)).decode('utf-8')
        if 'subscription' in input:
            user.subscription = json.dumps(input['subscription'])
        if 'loop_state' in input:

            if input['loop_state'] == 'stop':
                user.loop_state = 'stop'

            else:
                raise Exception(f"Exchange loop state is:{user.loop_state}, {input['loop_state']} not allowed")

        user.save()
        return UpdateUser(user=user)

class UpdateCoinGecko(graphene.Mutation):
    class Arguments:
        loop_state = graphene.String()
    
    coin_gecko = graphene.Field(CoinGeckoNode)

    @staticmethod
    def mutate(root, info, **input):
        coin_gecko = CoinGecko.objects().first()
        if 'loop_state' in input:

            if input['loop_state'] in ['stop', 'stopped']:
                coin_gecko.loop_state = input['loop_state']

            else:
                raise Exception(f"Exchange loop state is:{coin_gecko.loop_state}, {input['loop_state']} not allowed")

            coin_gecko.loop_state = input['loop_state']
            coin_gecko.save()

        return UpdateCoinGecko(coin_gecko=coin_gecko)

class UpdateExchange(graphene.Mutation):
    class Arguments:
        _id = graphene.String()
        name            = graphene.String()
        exchange_api    = graphene.String()
        instruments_url = graphene.String()
        loop_state      = graphene.String()

    exchange = graphene.Field(ExchangeNode)

    @staticmethod
    def mutate(root, info, **input):
        exchange = Exchange.objects(id=ObjectId(input['_id'])).first()

        if 'name' in input:
            exchange.name = input['name']
        if 'exchange_api' in input:
            exchange.exchange_api = input['exchange_api']
        if 'instruments_url' in input:
            exchange.instruments_url = input['instruments_url']
        if 'loop_state' in input:

            if input['loop_state'] in ['stop', 'stopped']:
                exchange.loop_state = input['loop_state']

            else:
                raise f"Exchange loop state is:{exchange.loop_state}, {input['loop_state']} not allowed"

            exchange.loop_state = input['loop_state']

        exchange.save()
        return UpdateExchange(exchange=exchange)


class AddSubscription(graphene.Mutation):
    class Arguments:
        endpoint            = graphene.String()
        expirationTime      = graphene.String()
        p256dh              = graphene.String()
        auth                = graphene.String()

    stuff = graphene.Field(graphene.String)

    @staticmethod
    def mutate(root, info, **input):
        sub = {"endpoint": input['endpoint'], "expirationTime": input['expirationTime'], "keys": {"p256dh": input['p256dh'], "auth": input['auth']}}
        user = info.context['user']
        user.subscription = sub
        user.save()
        return AddSubscription(stuff='worked')

class RemoveSubscription(graphene.Mutation):
    class Arguments:
        _id     = graphene.String()
        channel = graphene.String()

    exchange = graphene.Field(ExchangeNode)

    @staticmethod
    def mutate(root, info, **input):
        exchange = Exchange.objects(id=ObjectId(input['_id'])).first()
        exchange.subscriptions.append(input['channel'])
        exchange.save()
        return AddSubscription(exchange=exchange)