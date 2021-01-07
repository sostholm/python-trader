import motor.motor_asyncio
import asyncio

class Logger:
    initialized     = False
    collection      = None
    batching        = None
    batch_timeout   = 1
    name            = None
    log_to_console  = False

    def __init__(self, database, collection, username=None, password=None, url=None, port=None, loop=None, batching=None, batch_timeout=1, name='nameless', client=None, log_to_console=False):

        if not client:
            if not loop:
                loop = asyncio.get_running_loop()

            self.name = name
            self.client = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb://{username}:{password}@{url}:{port}', io_loop=loop)
        self.collection = getattr(getattr(client, database), collection)
        self.initialized = True
        self.log_to_console = False

    def console_log(self, msg):
        if self.log_to_console:
            print(msg)

    async def info(self, msg):
        self.console_log(msg)
        await self.collection.insert_one({'type': 'info', 'name': self.name, 'message': msg})

    async def warning(self, msg):
        self.console_log(msg)
        await self.collection.insert_one({'type': 'warning', 'name': self.name, 'message': msg})

    async def error(self, msg):
        self.console_log(msg)
        await self.collection.insert_one({'type': 'error', 'name': self.name, 'message': msg})
