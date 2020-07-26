import graphene
from models import UserNode, ExchangeNode, PositionNode, User, Position, Order, Exchange, CurrencyPair
from encrypt import password_encrypt, password_decrypt
import json
import bcrypt
from bson import ObjectId

class AddUser(graphene.Mutation):

    class Input:
        username    = graphene.String(required=True)
        password    = graphene.String(required=True)
        api_key     = graphene.String(required=True)
        secret      = graphene.String(required=True)

    user = graphene.Field(UserNode)

    @staticmethod
    def mutate(root, info, **input):
        bl = User(
            username    = input['username'],
            password    = bcrypt.hashpw(input['password'].encode(), bcrypt.gensalt(12)).decode('utf-8'),
            api_key     = password_encrypt(message=input['api_key'], password=input['password']).decode('utf-8'),
            secret      = password_encrypt(message=input['secret'], password=input['password']).decode('utf-8')
        )
        bl.save()
        return AddUser(user=bl)

class AddPosition(graphene.Mutation):
    class Arguments:
        user_id         = graphene.String()
        currency_pair   = graphene.String(required=True)
        held_currency   = graphene.String(required=True)
        amount          = graphene.Float(required=True)
        date            = graphene.types.datetime.DateTime()
        full_info       = graphene.types.json.JSONString()

    position = graphene.Field(Position)

    @staticmethod
    def mutate(root, info, **input):
        pb = Position(
                currency_pair   = input['currency_pair'],
                held_currency   = input['held_currency'],
                amount          = input['amount'],
                date            = input['date'],
                full_info       = input['full_info']
            )
        user = User.objects(id=input['user_id']).first()
        user.balance.append(pb).save()

        return AddPosition(position=pb)

class AddOrder(graphene.Mutation):
    class Arguments:
        user_id     = graphene.String()
        side        = graphene.String()
        fee         = graphene.Float()
        created_at  = graphene.types.datetime.DateTime()
        deal_price  = graphene.Float()
        avg_price   = graphene.Float()
        volume      = graphene.Float()
        price       = graphene.Float()
        status_msg  = graphene.String()
        remain_volume = graphene.Float()
        baseCoin    = graphene.String()
        countCoin   = graphene.String()
        status      = graphene.Int()
        all_details = graphene.types.json.JSONString()

    order = graphene.Field(Order)

    @staticmethod
    def mutate(root, info, **input):
        pb = Order(
            side        = input['side'],
            fee         = input['fee'],
            created_at  = input['created_at'],
            deal_price  = input['deal_price'],
            avg_price   = input['avg_price'],
            volume      = input['volume'],
            price       = input['price'],
            status_msg  = input['status_msg'],
            remain_volume = input['remain_volume'],
            baseCoin    = input['baseCoin'],
            countCoin   = input['countCoin'],
            status      = input['status'],
            all_details = input['all_details'],
        )
        user = User.objects(id=input['user_id']).first()
        user.orders.append(pb).save()

        return AddOrder(order=pb)

class AddExchange(graphene.Mutation):
    class Arguments:
        name            = graphene.String()
        exchange_api    = graphene.String()

    exchange = graphene.Field(ExchangeNode)

    @staticmethod
    def mutate(root, info, **input):
        obj = Exchange(
            name        = input['name'],
            exchange_api= input['exchange_api'],
        )
        obj.save()

        return AddExchange(exchange=obj)
        
class UpdateUser(graphene.Mutation):
    class Arguments:
        _id = graphene.String()
        password    = graphene.String()
        api_key     = graphene.String()
        secret      = graphene.String()

    user = graphene.Field(User)

    @staticmethod
    def mutate(root, info, **input):
        user = User.objects(id=ObjectId(input['_id'])).first()

        if 'password' in input:
            user.password   = bcrypt.hashpw(input['password'], bcrypt.gensalt(12)).decode('utf-8')
        if 'api_key' in input:
            user.api_key    = password_encrypt(message=input['api_key'], password=input['password']).decode('utf-8')
        if 'secret' in input:
            user.secret     = password_encrypt(message=input['secret'], password=input['password']).decode('utf-8')
        if 'subscription' in input:
            user.subscription = input['subscription']

        user.save()
        return UpdateUser(user=user)


class UpdateExchange(graphene.Mutation):
    class Arguments:
        _id             = graphene.String()
        name            = graphene.String()
        exchange_api    = graphene.String()
        loop_state      = graphene.String()

    exchange = graphene.Field(ExchangeNode)

    @staticmethod
    def mutate(root, info, **input):
        exchange = Exchange.objects(id=ObjectId(input['_id'])).first()

        if 'name' in input:
            exchange.name = input['name']
        if 'exchange_api' in input:
            exchange.exchange_api = input['exchange_api']
        if 'loop_state' in input:
            exchange.loop_state = input['loop_state']

        exchange.save()
        return UpdateExchange(exchange=exchange)


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
            exchange.loop_state = input['loop_state']

        exchange.save()
        return UpdateExchange(exchange=exchange)


class AddSubscription(graphene.Mutation):
    class Arguments:
        _id     = graphene.String()
        channel = graphene.String()

    exchange = graphene.Field(ExchangeNode)

    @staticmethod
    def mutate(root, info, **input):
        exchange = Exchange.objects(id=ObjectId(input['_id'])).first()
        exchange.subscriptions.append(input['channel'])
        
        if not CurrencyPair.objects(pair=input['channel']):
            cp = CurrencyPair(pair=input['channel'])
            exchange.currency_pairs.append(cp)
            cp.save()
        
        exchange.save()
        return AddSubscription(exchange=exchange)

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