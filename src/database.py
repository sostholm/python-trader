# from mongoengine import connect
import os
import motor.motor_asyncio
# from models import User, Position, Order

# connect('trader', host=f'mongodb://pine64:27017')

PASSWORD = None

if 'PASSWORD' in os.environ:
    PASSWORD = os.environ["PASSWORD"]
else:
    with open('/run/secrets/db_password', 'r') as file:
        PASSWORD = file.read().replace('\n', '')

def get_client(loop):
    return  motor.motor_asyncio.AsyncIOMotorClient(f'mongodb://root:{PASSWORD}@pine64:27017', io_loop=loop)
