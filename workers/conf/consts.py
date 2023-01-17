from solders.pubkey import Pubkey
import random

MAINNET_HTTP_URLS = [
    "https://prettiest-evocative-sailboat.solana-mainnet.quiknode.pro/",
    "https://broken-falling-dew.solana-mainnet.quiknode.pro/",
    "https://aged-boldest-tree.solana-mainnet.quiknode.pro/",
    "https://snowy-boldest-needle.solana-mainnet.quiknode.pro/",
    "https://practical-cosmopolitan-dream.solana-mainnet.quiknode.pro/",
    "https://evocative-young-forest.solana-mainnet.quiknode.pro/",
    "https://radial-magical-needle.solana-mainnet.quiknode.pro/",
    "https://prettiest-evocative-sailboat.solana-mainnet.quiknode.pro/",
    "https://sly-morning-meme.solana-mainnet.quiknode.pro/",
    "https://purple-restless-cloud.solana-mainnet.quiknode.pro/",
]
MAINNET_WSS_URL = "wss://solitary-quaint-fire.solana-mainnet.quiknode.pro/4fddcf75d9da1fa3a5606ec79e66048cf007bc22/"

MAINNET_HTTP_URL = random.choice(MAINNET_HTTP_URLS)


marketAddress = Pubkey.from_string("2jv2x2pA1B14cEfmptvEXFTLNcqabpkHBv8MnWCkhbeP")
balances = Pubkey.from_string("D2tc92Dbo8uAZ6tVtbDEaUo6wYFsHAR3fSu4hrYdmnH3")
bidTreeAddress = Pubkey.from_string("FstBzVA3ctHewFJXxUoXrgSNbooGt73MdF1XcJzigwpu")
askTreeAddress = Pubkey.from_string("BTCYzJXAHEKg7D7LhxhF3MBhJ1LSrxEy3HRL4Y6mSqHr")
wsolVault = Pubkey.from_string("BSd4oMiwMFkPjC2rAH72gVnTJyzuKmBJzJr5XSYxdGwZ")
feeReceiverAddress = Pubkey.from_string("ALbmFM1JnfK5ufcsdvvj5Ap1ohZnZuvC7yHe9iVHrzni")
lotVault = Pubkey.from_string("C85i6hX8LKXzEnzpe7WnVbmFFYZYF6MWqHsLPXZ9fpD5")
marketAuthPDA = Pubkey.from_string("6EmhG5d4kzh2JvjaQ9iFZ1MfNitXJfxp42952vRaRMMN")
PROGRAM_ID = Pubkey.from_string("833pSHchW8AWggrvx8394HHkH1cMHxdyYcDro8ABYUXC")
lotsMint = Pubkey.from_string("224N1QgiHV6xizsazZUZjujvrfQP62VWE5XyMdmoVit2")
buyOrderLog = Pubkey.from_string("HDP3RccuKx5eBvdCcE8JVpiFkXCvsGdkczHA6qBkcp3Q")
sellOrderLog = Pubkey.from_string("H13zkvb1uiAbeybEMqW8cRTXzFE7khViRaFuWW5eFUmo")
bidLog = Pubkey.from_string("FJ2Wdob1DJq6QW5Fy6x97b5JhaZZBt3cZ9a9Np1UcYLR")
askLog = Pubkey.from_string("9nBKYi2C8dVTwTXuzHyfvt7kGdT7gQUCQYukyNZbHjGQ")

# TIMERS
MAIN_BREAK_SLEEP = 2
MSG_RX_TIMEOUT = 0.005
MAIN_LOOP_SLEEP = 0.001
TRADES_PER_MINUTES = 2
MAIN_REPORT_PERIOD = 5
POLL_TIME_SEC = 0.001
