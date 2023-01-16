from collections import defaultdict
from workers.utils.gigadex_client.accounts.order_tree import OrderTree
from solana.rpc.types import DataSliceOpts
from solana.rpc.async_api import AsyncClient
from workers.conf import consts as cn
from solana.rpc.commitment import Confirmed


def extract_nodes(arr):
    nodes = [{'price': n.price, 'amount': n.amount, 'uid': n.uid} for n in arr]
    return nodes


async def get_orderbooks(get_asks=True, get_bids=True):
    async with AsyncClient(cn.MAINNET_HTTP_URL) as client:
        if get_bids:
            _bids = await OrderTree.fetch(client, cn.bidTreeAddress, commitment=Confirmed, program_id=cn.PROGRAM_ID)
            bids = extract_nodes(_bids.nodes)
        if get_asks:
            _asks = await OrderTree.fetch(client, cn.askTreeAddress, commitment=Confirmed, program_id=cn.PROGRAM_ID)
            asks = extract_nodes(_asks.nodes)
        if get_asks and get_bids:
            return bids, asks
        elif get_asks:
            return asks
        elif get_bids:
            return bids
        else:
            raise Exception(f"Must request either asks, bids, or both")


async def get_balances():
    async with AsyncClient(cn.MAINNET_HTTP_URL) as client:
        num_info = await client.get_account_info(cn.balances, data_slice=DataSliceOpts(8, 8))
        num_users = int.from_bytes(num_info.value.data, 'little')
        balances_info = await client.get_account_info(cn.balances, data_slice=DataSliceOpts(16, 16*num_users))
        balances_data = balances_info.value.data
        balances = {}
        for i in range(num_users):
            idx = i * 16 + 16
            lamports = int.from_bytes(balances_data[idx:idx+8], 'little')
            idx += 8
            lots = int.from_bytes((balances_data[idx:idx+8]), 'little')
            balances[i+1] = [lamports, lots]
        return balances


def get_compressed_orderbook(nodes, is_ask=True):
    book = defaultdict(lambda: 0)
    for n in nodes:
        price = n['price']
        if price > 0:
            book[n['price']] += n['amount']
    comp = list(book.items())
    comp.sort(key=lambda x: x[0], reverse=is_ask)
    return comp
