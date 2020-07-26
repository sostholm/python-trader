from mongoengine import connect
import os

from models import User, Position, Order

connect('trader', host=f'mongodb://pine64:27017')