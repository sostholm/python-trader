import graphene
from models import UserNode, PositionNode, OrderNode, User, Position, Order
import json

class AddUser(graphene.Mutation):

    class Input:
        username    = graphene.String(required=True)
        password    = graphene.String(required=True)
        api_key     = graphene.String(required=True)
        secret      = graphene.String(required=True)

    user = graphene.Field(User)

    @staticmethod
    def mutate(root, info, **input):
        bl = User(
            username    = input['username'],
            password    = input['password'],
            api_key     = input['api_key'],
            secret      = input['secret']
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
        deal_price  = graphene.Float()()
        avg_price   = graphene.Float()()
        volume      = graphene.Float()()
        price       = graphene.Float()()
        status_msg  = graphene.String()()
        remain_volume = graphene.Float()()
        baseCoin    = graphene.String()()
        countCoin   = graphene.String()()
        status      = graphene.Int()
        all_details = graphene.types.json.JSONString()

    order = graphene.Field(OrderNode)

    @staticmethod
    def mutate(root, info, **input):
        pb = OrderNode(
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



class UpdateUser(graphene.Mutation):
    class Arguments:
        _id = graphene.String()
        password    = graphene.String()
        api_key     = graphene.String()
        secret      = graphene.String()

    user = graphene.Field(User)

    @staticmethod
    def mutate(root, info, **input):
        user = User.objects(id=input['_id']).first()
        if 'password' in input:
            pass
        if 'api_key' in input:
            pass
        if 'secret' in input:
            pass
        user.save()
        return UpdateUser(user=user)