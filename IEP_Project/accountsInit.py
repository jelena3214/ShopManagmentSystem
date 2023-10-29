import os
from web3 import Web3
from web3 import Account
from web3 import HTTPProvider

GANACHE_URL = 'http://127.0.0.1:8545'
w3 = Web3(HTTPProvider(GANACHE_URL))

with open('keys.json', 'r') as file:
    private_key = Account.decrypt(file.read(), 'asdasdasd').hex()

owner_account = Account.from_key(private_key)


result = w3.eth.send_transaction({
    'from' : w3.eth.accounts[0],
    'to' : owner_account.address,
    'value' : w3.to_wei(80, 'ether')
})