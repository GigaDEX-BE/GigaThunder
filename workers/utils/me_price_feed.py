import asyncio
import aiohttp


async def get_highest_bid_async(symbol='gigadao'):
    url = f"https://api-mainnet.magiceden.dev/v2/mmm/pools?collectionSymbol={symbol}&limit=500&offset=0&filterOnSide=1&hideExpired=true&direction=1&field=5"
    async with aiohttp.ClientSession() as session:
        payload = {}
        headers = {}
        async with session.get(url, headers=headers, data=payload) as resp:
            data = await resp.json()
            results = data['results']
            if len(results) < 1:
                return None
            price = results[0]['spotPrice']
            return price


async def get_lowest_ask_async():
    url = f"http://api-mainnet.magiceden.dev/v2/collections/gigadao/stats"
    async with aiohttp.ClientSession() as session:
        payload = {}
        headers = {}
        async with session.get(url, headers=headers, data=payload) as resp:
            result = await resp.json()
            return result['floorPrice']


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    lowest_ask = loop.run_until_complete(get_lowest_ask_async())
    highest_bid = loop.run_until_complete(get_highest_bid_async())
    print(f"lowest ask: {lowest_ask}")
    print(f"highest bid: {highest_bid}")


