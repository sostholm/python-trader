from mongoengine import connect
import os

from models import User, Position, Order

connect('ProjectTrader', host=f'mongodb://pine64:27017')