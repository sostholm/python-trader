import motor.motor_asyncio
import asyncio

class Logger:
    initialized     = False
    collection      = None
    batching        = None
    batch_timeout   = 1
    name            = None

    def __init__(self, username, password, url, port, database, collection, loop=None, batching=None, batch_timeout=1, name='nameless', client=None):

        if not client:
            if not loop:
                loop = asyncio.get_running_loop()

            self.name = name
            self.client = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb://{username}:{password}@{url}:{port}', io_loop=loop)
        self.collection = getattr(getattr(client, database), collection)
        self.initialized = True

    async def info(self, msg):
        
        await self.collection.insert_one({'type': 'info', 'name': self.name, 'message': msg})

    async def warning(self, msg):
        
        await self.collection.insert_one({'type': 'warning', 'name': self.name, 'message': msg})

    async def error(self, msg):

        await self.collection.insert_one({'type': 'error', 'name': self.name, 'message': msg})
