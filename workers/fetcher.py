import asyncio
import time
import traceback
from workers.utils.me_price_feed import get_highest_bid_async, get_lowest_ask_async
from multiprocessing.connection import Connection
from workers.conf import consts as cn
import logging
logging.basicConfig(level=logging.INFO)

FETCH_PERIOD_SEC = 5


class Fetcher:
    def __init__(self, traderConn, guiConn):
        self.traderConn: Connection = traderConn
        self.guiConn: Connection = guiConn

        self.txd = []
        self.rxd = []

    async def run_loop(self):
        last_fetch_ts = 0
        while True:
            try:
                ts = time.time()
                if (ts - last_fetch_ts) > FETCH_PERIOD_SEC:
                    last_fetch_ts = ts
                    me_highest_bid, me_lowest_ask = await asyncio.gather(get_highest_bid_async(), get_lowest_ask_async())
                    me_bid = me_highest_bid / 1e9
                    me_ask = me_lowest_ask / 1e9
                    self.guiConn.send((me_bid, me_ask))
                await asyncio.sleep(cn.MAIN_LOOP_SLEEP)
            except:
                logging.error(traceback.format_exc())
                await asyncio.sleep(cn.MAIN_BREAK_SLEEP)
                await self.run_loop()


def fetcher_process(traderConn, guiConn):
    loop = asyncio.new_event_loop()
    reporter = Fetcher(traderConn, guiConn)
    loop.run_until_complete(reporter.run_loop())
