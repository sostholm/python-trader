from aiohttp.client import request
import graphene
import aiohttp
import json
from .meta_exchange import MetaExchange, Ticker, Balance, Order, make_coins
from web3 import Web3
import asyncio
import concurrent
import functools
from bson import ObjectId

from .abi import ERC20_ABI
w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/0a70e18832ec4e57bc405216c585eeb4'))

def get_token_balance(address, token_contract):
    abi = ERC20_ABI
    try:
        contract = w3.eth.contract(token_contract, abi=abi)
    except Exception as e:
        token_contract = Web3.toChecksumAddress(token_contract)
        contract = w3.eth.contract(token_contract, abi=abi)

    decimals = contract.functions.decimals().call()
    DECIMALS = 10 ** decimals
    contract.functions.totalSupply().call() // DECIMALS
    raw_balance = contract.functions.balanceOf(address).call()
    
    balance     = raw_balance / DECIMALS
    name        = contract.functions.name().call()
    symbol      = contract.functions.symbol().call()
    
    return {"name": name, "symbol": symbol, "balance": balance}

async def make_async(wallet, token_contract):
    
    loop = asyncio.get_running_loop() 
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool, functools.partial(get_token_balance, wallet, token_contract)
        )
        return result

class Ethereum(graphene.ObjectType):
    class Meta:
        interfaces = (MetaExchange,)

    async def resolve_balance(self, info, api_key="", api_secret=""):

        wallets = info.context['user']['wallets']
        
        if len(wallets) == 0:
            raise Exception('User have no wallets')

        balances = []
        for wallet in wallets:
            for f in asyncio.as_completed([make_async(wallet.address, i) for i in wallet.tokens]):
                balances.append(await f)
        
        coins = []
        if len(balances) > 0:
            coins = make_coins(info.context, balances, 'symbol', 'balance', 'balance')
        return coins

    async def resolve_orders(self, info, order_type=""):
        return {}

    async def resolve_tickers(self, info):
        return {}
