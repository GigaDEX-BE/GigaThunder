import asyncio
import time
from multiprocessing.connection import Connection
from asyncio.exceptions import TimeoutError
from solana.rpc.websocket_api import connect
from solana.rpc.commitment import Confirmed
from solana.rpc.websocket_api import SolanaWsClientProtocol
from workers.utils.gigadex_client.accounts.market_order_log import MarketOrderLog
from workers.conf import consts as cn
import traceback
from solders.rpc.responses import AccountNotification, SubscriptionResult
import os
from dotenv import load_dotenv
import logging
load_dotenv()
logging.basicConfig(level=logging.INFO)


async def with_timout(coro, _timeout):
    try:
        data = await asyncio.wait_for(coro, timeout=_timeout)
        return data
    except TimeoutError:
        return []


class Subscriber:
    def __init__(self, tx_conn):
        self.tx_conn: Connection = tx_conn
        self.num_notifications = 0
        self.notifications = []

    async def run_loop(self):
        try:
            custom_rpc_ws = os.environ.get("custom_rpc_ws")
            logging.info(f"Initializing Subscriber Process with ws: {custom_rpc_ws}")
            ws = await connect(custom_rpc_ws, max_size=int(2e9))
            sol_websocket: SolanaWsClientProtocol = ws
            await sol_websocket.account_subscribe(cn.buyOrderLog, encoding='base64', commitment=Confirmed)
            while True:
                ###########################################################
                # Check for new data
                data = await with_timout(sol_websocket.recv(), cn.MSG_RX_TIMEOUT)
                for msg in data:
                    if isinstance(msg, SubscriptionResult):
                        logging.info(f"Subscribed to buyOrderLog: {msg}")
                    elif isinstance(msg, AccountNotification):
                        msg_bytes = msg.result.value.data
                        sell_log = MarketOrderLog.decode(msg_bytes)
                        if sell_log.amount == 1:
                            msg = {'price': sell_log.total_value_lamports, 'ts': time.time()}

                            logging.info(f"got msg: {msg}")
                            self.num_notifications += 1
                            self.notifications.append(msg)

                            # TODO do something with this to aggregate in main...
                            # self.tx_conn.send(msg)

                    else:
                        logging.error(f"UNKNOWN MSG TYPE: {type(msg)}")
                await asyncio.sleep(cn.MAIN_LOOP_SLEEP)
        except Exception:
            logging.error(traceback.format_exc())
            try:
                await sol_websocket.close()
            except Exception:
                pass
            await asyncio.sleep(cn.MAIN_BREAK_SLEEP)
            logging.info("reconnecting")
            await self.run_loop()


def subscriber_process(tx_conn):
    loop = asyncio.new_event_loop()
    subscriber = Subscriber(tx_conn)
    loop.run_until_complete(subscriber.run_loop())

