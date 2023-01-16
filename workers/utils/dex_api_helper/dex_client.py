# we'll see...
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from workers.conf import consts
from solana.rpc.commitment import Confirmed
from workers import utils
import random


class GigaDexClient:

    def __init__(self, lot_account, priv):
        rpc_url = consts.MAINNET_HTTP_URL
        self.async_rpc_client = AsyncClient(rpc_url, commitment=Confirmed)
        self.keypair = Keypair.from_seed(bytes.fromhex(priv))
        self.lot_account = Pubkey.from_string(lot_account)

    async def randomize_rpc(self):
        self.async_rpc_client = AsyncClient(random.choice(consts.MAINNET_HTTP_URLS), commitment=Confirmed)

    async def limit_buy(self, price, amount):
        tx = await utils.rpc.run_limit_buy(price, amount, self.async_rpc_client, self.keypair)
        return tx

    async def limit_sell(self, price, amount):
        _tx = await utils.rpc.run_limit_sell(price, amount, self.lot_account, self.async_rpc_client, self.keypair)
        return _tx

    async def market_buy(self, amount):
        tx = await utils.rpc.run_market_buy(amount, self.async_rpc_client, self.keypair)
        return tx

    async def market_sell(self, amount):
        tx = await utils.rpc.run_market_sell(amount, self.lot_account, self.async_rpc_client, self.keypair)
        return tx

    async def cancel_limit_buy(self, price):
        tx = await utils.rpc.run_cancel_limit_buy(price, self.async_rpc_client, self.keypair)
        return tx

    async def cancel_limit_sell(self, price):
        tx = await utils.rpc.run_cancel_limit_sell(price, self.async_rpc_client, self.keypair)
        return tx

    async def claim_balance(self):
        tx = await utils.rpc.run_claim_balance(self.lot_account, self.async_rpc_client, self.keypair)
        return tx

    async def get_wallet_balance(self):
        balances = await utils.get_wallet_balances(self.async_rpc_client, self.keypair)
        return balances

    async def create_user_account(self):
        tx = await utils.rpc.run_create_user_account(self.async_rpc_client, self.keypair)
        return tx

    async def limit_sell_market_buy(self, price, amount):
        tx = await utils.rpc.run_limit_sell_market_buy(price, amount, self.lot_account,
                                                       self.async_rpc_client, self.keypair)
        return tx

    async def limit_buy_market_sell(self, price, amount):
        tx = await utils.rpc.run_limit_buy_market_sell(price, amount, self.lot_account,
                                                       self.async_rpc_client, self.keypair)
        return tx
