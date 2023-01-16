import asyncio
from workers.utils.get_full_state import get_orderbooks

INTER_TRY_SLEEP_SEC = 2


async def run_cancel_all(dexClient, uid):

    bids_nodes, asks_nodes = await get_orderbooks()

    # get open orders for my uid
    my_bids = list(filter(lambda x: x['uid'] == uid, bids_nodes))
    my_asks = list(filter(lambda x: x['uid'] == uid, asks_nodes))

    no_open_limits = len(my_asks) == 0 and len(my_bids) == 0
    print(f"no open limits: {no_open_limits}")

    if no_open_limits:
        return True
    else:

        bid_prices = [x['price'] for x in my_bids]
        ask_prices = [x['price'] for x in my_asks]

        # cancel open orders
        for price in bid_prices:
            tx = await dexClient.cancel_limit_buy(price)
            print(f"got cancel bid tx: {tx}")

        for price in ask_prices:
            tx = await dexClient.cancel_limit_sell(price)
            print(f"got cancel ask tx: {tx}")
