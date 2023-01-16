from solana.rpc.types import TokenAccountOpts
from workers.conf.consts import lotsMint as LOTS_MINT


async def get_wallet_balances(async_client, keypair):
    account_info = await async_client.get_account_info(keypair.pubkey())
    account_balance_lamports = account_info.value.lamports
    opts = TokenAccountOpts(mint=LOTS_MINT)
    token_accounts = await async_client.get_token_accounts_by_owner_json_parsed(keypair.pubkey(), opts)
    values = token_accounts.value
    lot_accounts = []
    total_lots = 0
    for act in values:
        token_account = act.pubkey
        amount = int(act.account.data.parsed['info']['tokenAmount']['amount'])
        lot_accounts.append({'address': token_account, 'amount': amount})
        total_lots += amount
    return {
        'lamports': account_balance_lamports,
        'total_lots': total_lots,
        'lot_accounts': lot_accounts
    }

