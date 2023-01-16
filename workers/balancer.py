from conf import consts as cn
import asyncio
import logging
logging.basicConfig(level=logging.INFO)


class Balancer:
    def __init__(self, tx_conn):
        self.tx_conn = tx_conn

    async def run_loop(self):

        # TODO cancel and claim and 1/2 trade frequency or lower

        await asyncio.sleep(cn.MAIN_LOOP_SLEEP)


def balancer_process(tx_conn):
    loop = asyncio.new_event_loop()
    balancer = Balancer(tx_conn)
    loop.run_until_complete(balancer.run_loop())


