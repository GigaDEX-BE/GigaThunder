from workers.conf import consts as cn
from anchorpy.provider import Wallet
from anchorpy import Provider
from solders.pubkey import Pubkey
from solana.transaction import Transaction

from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT as SYSVAR_RENT_PUBKEY


from gigadex_client import instructions
from gigadex_client.program_id import PROGRAM_ID
from spl.token.constants import TOKEN_PROGRAM_ID, WRAPPED_SOL_MINT
from spl.token.async_client import AsyncToken
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Confirmed, Finalized

fastOpts = TxOpts(skip_preflight=True, preflight_commitment=Confirmed)
slowOpts = TxOpts(skip_preflight=False, preflight_commitment=Finalized)


async def run_create_user_account(async_client, keypair):
    """
    This needs to be run once per user per market.
    It assigns them a market specific UID and an entry in the market's "balances" account from which they can withdraw.
    """
    wallet = Wallet(keypair)
    provider = Provider(async_client, wallet, opts=fastOpts)
    user_pda, _ = Pubkey.find_program_address([cn.marketAddress.__bytes__(),
                                                  keypair.pubkey().__bytes__()], PROGRAM_ID)
    accounts = {
        'signer': keypair.pubkey(),
        'market': cn.marketAddress,
        'balances': cn.balances,
        'user': user_pda,
        'system_program': SYS_PROGRAM_ID,
        'rent': SYSVAR_RENT_PUBKEY,
    }
    ix = instructions.create_account(accounts)
    tx = Transaction().add(ix)
    tx_result = await provider.send(tx, [keypair], opts=fastOpts)
    return tx_result


async def run_limit_buy(price, amount, async_client, keypair):

    wallet = Wallet(keypair)
    provider = Provider(async_client, wallet, opts=fastOpts)
    user_pda, _ = Pubkey.find_program_address([cn.marketAddress.__bytes__(),
                                                  keypair.pubkey().__bytes__()], PROGRAM_ID)
    args = {
        'price': price,
        'amount': amount
    }
    accounts = {
        'signer': keypair.pubkey(),
        'user': user_pda,
        'market': cn.marketAddress,
        'bid_tree': cn.bidTreeAddress,
        'ask_tree': cn.askTreeAddress,
        'wsol_vault': cn.wsolVault,
        'bid_logs': cn.bidLog,
        'token_program': TOKEN_PROGRAM_ID,
        'system_program': SYS_PROGRAM_ID,
    }
    ix = instructions.limit_buy(args, accounts)
    tx = Transaction().add(ix)
    tx_result = await provider.send(tx, [keypair], opts=fastOpts)
    return tx_result


async def run_cancel_limit_buy(price, async_client, keypair):
    wallet = Wallet(keypair)
    provider = Provider(async_client, wallet, opts=fastOpts)
    user_pda, _ = Pubkey.find_program_address([cn.marketAddress.__bytes__(),
                                                  keypair.pubkey().__bytes__()], PROGRAM_ID)
    args = {'price': price}
    accounts = {
        'signer': keypair.pubkey(),
        'user': user_pda,
        'market': cn.marketAddress,
        'bid_tree': cn.bidTreeAddress,
        'balances': cn.balances,
        'bid_logs': cn.bidLog,
        'system_program': SYS_PROGRAM_ID,
    }
    ix = instructions.cancel_limit_buy(args, accounts)
    tx = Transaction().add(ix)
    tx_result = await provider.send(tx, [keypair], opts=fastOpts)
    return tx_result


async def run_limit_sell(price, amount, sender_lot_ata, async_client, keypair):
    wallet = Wallet(keypair)
    provider = Provider(async_client, wallet, opts=fastOpts)
    user_pda, _ = Pubkey.find_program_address([cn.marketAddress.__bytes__(),
                                                  keypair.pubkey().__bytes__()], PROGRAM_ID)
    args = {
        'price': price,
        'amount': amount
    }
    accounts = {
        'signer': keypair.pubkey(),
        'user': user_pda,
        'market': cn.marketAddress,
        'ask_tree': cn.askTreeAddress,
        'bid_tree': cn.bidTreeAddress,
        'lot_vault': cn.lotVault,
        'sender_lot_ata': sender_lot_ata,
        'ask_logs': cn.askLog,
        'system_program': SYS_PROGRAM_ID,
        'rent': SYSVAR_RENT_PUBKEY,
    }
    ix = instructions.limit_sell(args, accounts)
    tx = Transaction().add(ix)
    tx_result = await provider.send(tx, [keypair], opts=fastOpts)
    return tx_result


async def run_cancel_limit_sell(price, async_client, keypair):
    user_pda, _ = Pubkey.find_program_address([cn.marketAddress.__bytes__(),
                                                  keypair.pubkey().__bytes__()], PROGRAM_ID)
    wallet = Wallet(keypair)
    provider = Provider(async_client, wallet, opts=fastOpts)
    args = {'price': price}
    accounts = {
        'signer': keypair.pubkey(),
        'user': user_pda,
        'market': cn.marketAddress,
        'ask_tree': cn.askTreeAddress,
        'balances': cn.balances,
        'ask_logs': cn.askLog,
        'system_program': SYS_PROGRAM_ID,
    }
    ix = instructions.cancel_limit_sell(args, accounts)
    tx = Transaction().add(ix)
    tx_result = await provider.send(tx, [keypair], opts=fastOpts)
    return tx_result


async def run_claim_balance(receiver_lot_ata, async_client, keypair):
    wsolMint = AsyncToken(async_client, WRAPPED_SOL_MINT, TOKEN_PROGRAM_ID, keypair)
    receiverWsolAta = await wsolMint.create_account(keypair.pubkey())
    if receiver_lot_ata is None:
        lotMint = AsyncToken(async_client, cn.lotsMint, TOKEN_PROGRAM_ID, keypair)
        receiver_lot_ata = await lotMint.create_account(keypair.pubkey())
    wallet = Wallet(keypair)
    provider = Provider(async_client, wallet, opts=fastOpts)
    user_pda, _ = Pubkey.find_program_address([cn.marketAddress.__bytes__(),
                                                  keypair.pubkey().__bytes__()], PROGRAM_ID)
    accounts = {
        'signer': keypair.pubkey(),
        'user': user_pda,
        'market': cn.marketAddress,
        'balances': cn.balances,
        'market_auth_pda': cn.marketAuthPDA,
        'wsol_vault': cn.wsolVault,
        'lot_vault': cn.lotVault,
        'receiver_wsol_ata': receiverWsolAta,
        'receiver_lot_ata': receiver_lot_ata,
        'system_program': SYS_PROGRAM_ID,
        'token_program': TOKEN_PROGRAM_ID,
        'rent': SYSVAR_RENT_PUBKEY,
    }
    ix = instructions.claim_balance(accounts)
    tx = Transaction().add(ix)
    tx_result = await provider.send(tx, [keypair], opts=fastOpts)
    return tx_result


async def run_market_buy(amount, async_client, keypair):
    wallet = Wallet(keypair)
    provider = Provider(async_client, wallet, opts=fastOpts)
    user_pda, _ = Pubkey.find_program_address([cn.marketAddress.__bytes__(),
                                                  keypair.pubkey().__bytes__()], PROGRAM_ID)
    args = {
        'amount': amount
    }
    accounts = {
        'signer': keypair.pubkey(),
        'user': user_pda,
        'market': cn.marketAddress,
        'balances': cn.balances,
        'ask_tree': cn.askTreeAddress,
        'wsol_vault': cn.wsolVault,
        'fee_receiver_address': cn.feeReceiverAddress,
        'buy_order_log': cn.buyOrderLog,
        'ask_logs': cn.askLog,
        'token_program': TOKEN_PROGRAM_ID,
        'system_program': SYS_PROGRAM_ID,
    }
    ix = instructions.market_buy(args, accounts)
    tx = Transaction().add(ix)
    tx_result = await provider.send(tx, [keypair], opts=fastOpts)
    return tx_result


async def run_market_sell(amount, sender_lot_ata, async_client, keypair):
    wallet = Wallet(keypair)
    provider = Provider(async_client, wallet, opts=fastOpts)
    user_pda, _ = Pubkey.find_program_address([cn.marketAddress.__bytes__(),
                                                  keypair.pubkey().__bytes__()], PROGRAM_ID)
    args = {
        'amount': amount
    }
    accounts = {
        'signer': keypair.pubkey(),
        'user': user_pda,
        'market': cn.marketAddress,
        'balances': cn.balances,
        'bid_tree': cn.bidTreeAddress,
        'sender_lot_ata': sender_lot_ata,
        'lot_vault': cn.lotVault,
        'fee_receiver_address': cn.feeReceiverAddress,
        'sell_order_log': cn.sellOrderLog,
        'bid_logs': cn.bidLog,
        'token_program': TOKEN_PROGRAM_ID,
        'system_program': SYS_PROGRAM_ID,
    }
    ix = instructions.market_sell(args, accounts)
    tx = Transaction().add(ix)
    tx_result = await provider.send(tx, [keypair], opts=fastOpts)
    return tx_result


#################################################################################################
#################################################################################################
#################################################################################################
async def run_limit_sell_market_buy(price, amount, sender_lot_ata, async_client, keypair):
    wallet = Wallet(keypair)
    provider = Provider(async_client, wallet, opts=fastOpts)
    user_pda, _ = Pubkey.find_program_address([cn.marketAddress.__bytes__(),
                                                  keypair.pubkey().__bytes__()], PROGRAM_ID)

    # limit sell ix
    args = {
        'price': price,
        'amount': amount
    }
    accounts = {
        'signer': keypair.pubkey(),
        'user': user_pda,
        'market': cn.marketAddress,
        'ask_tree': cn.askTreeAddress,
        'bid_tree': cn.bidTreeAddress,
        'lot_vault': cn.lotVault,
        'sender_lot_ata': sender_lot_ata,
        'ask_logs': cn.askLog,
        'system_program': SYS_PROGRAM_ID,
        'rent': SYSVAR_RENT_PUBKEY,
    }
    limit_sell_ix = instructions.limit_sell(args, accounts)

    # market buy ix
    args = {
        'amount': amount
    }
    accounts = {
        'signer': keypair.pubkey(),
        'user': user_pda,
        'market': cn.marketAddress,
        'balances': cn.balances,
        'ask_tree': cn.askTreeAddress,
        'wsol_vault': cn.wsolVault,
        'fee_receiver_address': cn.feeReceiverAddress,
        'buy_order_log': cn.buyOrderLog,
        'ask_logs': cn.askLog,
        'token_program': TOKEN_PROGRAM_ID,
        'system_program': SYS_PROGRAM_ID,
    }
    market_buy_ix = instructions.market_buy(args, accounts)

    # create tx
    tx = Transaction()
    tx.add(limit_sell_ix)
    tx.add(market_buy_ix)
    tx_result = await provider.send(tx, [keypair], opts=fastOpts)
    return tx_result


async def run_limit_buy_market_sell(price, amount, sender_lot_ata, async_client, keypair):
    wallet = Wallet(keypair)
    provider = Provider(async_client, wallet, opts=fastOpts)
    user_pda, _ = Pubkey.find_program_address([cn.marketAddress.__bytes__(),
                                                  keypair.pubkey().__bytes__()], PROGRAM_ID)

    # limit sell ix
    args = {
        'price': price,
        'amount': amount
    }
    accounts = {
        'signer': keypair.pubkey(),
        'user': user_pda,
        'market': cn.marketAddress,
        'bid_tree': cn.bidTreeAddress,
        'ask_tree': cn.askTreeAddress,
        'wsol_vault': cn.wsolVault,
        'bid_logs': cn.bidLog,
        'token_program': TOKEN_PROGRAM_ID,
        'system_program': SYS_PROGRAM_ID,
    }
    limit_buy_ix = instructions.limit_buy(args, accounts)

    # market sell ix
    args = {
        'amount': amount
    }
    accounts = {
        'signer': keypair.pubkey(),
        'user': user_pda,
        'market': cn.marketAddress,
        'balances': cn.balances,
        'bid_tree': cn.bidTreeAddress,
        'sender_lot_ata': sender_lot_ata,
        'lot_vault': cn.lotVault,
        'fee_receiver_address': cn.feeReceiverAddress,
        'sell_order_log': cn.sellOrderLog,
        'bid_logs': cn.bidLog,
        'token_program': TOKEN_PROGRAM_ID,
        'system_program': SYS_PROGRAM_ID,
    }
    market_sell_ix = instructions.market_sell(args, accounts)

    # create tx
    tx = Transaction()
    tx.add(limit_buy_ix)
    tx.add(market_sell_ix)
    tx_result = await provider.send(tx, [keypair], opts=fastOpts)
    return tx_result





