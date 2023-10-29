import os
from web3 import Web3
from web3 import Account
from web3 import HTTPProvider

GANACHE_URL = 'http://127.0.0.1:8545'
w3 = Web3(HTTPProvider(GANACHE_URL))

with open('customer.json', 'r') as file:
    private_key = Account.decrypt(file.read(), 'jelena123').hex()

customer_account = Account.from_key(private_key)


result = w3.eth.send_transaction({
    'from' : w3.eth.accounts[1],
    'to' : customer_account.address,
    'value' : w3.to_wei(80, 'ether')
})

result = w3.eth.send_transaction({
    'from' : w3.eth.accounts[2],
    'to' : customer_account.address,
    'value' : w3.to_wei(80, 'ether')
})

result = w3.eth.send_transaction({
    'from' : w3.eth.accounts[3],
    'to' : customer_account.address,
    'value' : w3.to_wei(80, 'ether')
})