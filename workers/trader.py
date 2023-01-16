import time
from conf import consts as cn
import asyncio
import random
import os
import traceback
import logging
from multiprocessing.connection import Connection
from workers.utils.dex_api_helper.dex_client import GigaDexClient
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.INFO)


class Trader:
    def __init__(self, tx_conn):
        self.tx_conn: Connection = tx_conn

        # init dex client
        pkstr = os.environ.get("pk_secret_hex")
        lot_account_pk_str = os.environ.get("lot_account_pk_str")
        # TODO internal trade rotation?
        self.dexClient = GigaDexClient(lot_account_pk_str, pkstr)
        self.inter_trade_period_sec = 60 / cn.TRADES_PER_MINUTES
        self.last_trade_time = 0
        self.num_trades = 0

    # DATA RTT TESTERS
    async def run_loop(self):
        try:
            while True:
                if (time.time() - self.last_trade_time) > self.inter_trade_period_sec:
                    bid_price = int(40e6) + random.randint(1, int(1e6))
                    tx = await self.dexClient.limit_buy_market_sell(bid_price, 1)
                    self.num_trades += 1
                    self.last_trade_time = time.time()
                    logging.info(f"placed bid for {bid_price} with tx: {tx} and {self.last_trade_time}")
                    msg = {'price': bid_price, 'ts': self.last_trade_time}
                    self.tx_conn.send(msg)
                await asyncio.sleep(cn.MAIN_LOOP_SLEEP)
        except Exception as _e:
            logging.error(traceback.format_exception())
            await asyncio.sleep(cn.MAIN_BREAK_SLEEP)
            await self.run_loop()


def trader_process(tx_conn):
    loop = asyncio.new_event_loop()
    trader = Trader(tx_conn)
    loop.run_until_complete(trader.run_loop())









