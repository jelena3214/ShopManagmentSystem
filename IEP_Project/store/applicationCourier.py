from functools import wraps
from flask import Flask, jsonify, make_response, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt
from configuration import Configuration
from models import *
import os
from web3 import Web3
from eth_utils import is_address
from web3 import Account

GANACHE_URL = os.environ["GANACHE_URL"]
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

application = Flask(__name__)
application.config.from_object(Configuration)
migrate = Migrate(application, database)

@application.route("/", methods = ["GET"])
def hello_world():
    return "<h1>Hello world!</h1>"

database.init_app(application)

jwt = JWTManager (application)

# If we have to provide this services just for couriers
def require_courier_token(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if not claims or "role" not in claims or claims["role"] != "Kurir":
            return jsonify(msg="Missing Authorization Header"), 401
        return fn(*args, **kwargs)
    return wrapper

@application.route("/orders_to_deliver", methods = ['GET'])
@require_courier_token
def orders_to_deliver():
    orders = Order.query.filter(Order.status == 'CREATED').all()
    order_data = []
    for order in orders:
        order_info = {
            "id": order.id,
            "email": order.email
        }
        order_data.append(order_info)

    response = {
        "orders": order_data
    }
    return jsonify(response), 200


def read_file(path):
    with open(path, 'r') as file:
        return file.read()
    
with open('keys.json', 'r') as file:
    private_key = Account.decrypt(file.read(), 'asdasdasd').hex()

owner_account = Account.from_key(private_key)

@application.route("/pick_up_order", methods = ["POST"])
@require_courier_token
def pick_up_order():
    if 'id' not in request.json:
        return jsonify(message = 'Missing order id.'), 400
    try:
        id = int(request.json['id'])
    except Exception:
        return jsonify(message = 'Invalid order id.'), 400
    
    order = Order.query.filter(Order.id == id).first()
    if id <=0 or order is None or order.status != 'CREATED':
        return jsonify(message = 'Invalid order id.'), 400
    
    if 'address' not in request.json or len(request.json['address']) == 0:
        return jsonify(message = 'Missing address.'), 400
    
    if not is_address(request.json['address']):
        return jsonify(message = 'Invalid address.'), 400

    abi = read_file('../../../sources/DeliveryContract.abi')
    contract = w3.eth.contract(address=order.contract_hash, abi=abi)

    try:
        transaction = contract.functions.assignCourier(Web3.to_checksum_address(request.json['address'])).build_transaction({
            'from': owner_account.address,
            'gasPrice': 2100,
            'nonce': w3.eth.get_transaction_count(owner_account.address)
        })

        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=owner_account.key.hex())
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Wait for the transaction to be mined
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        print('Transakcija uspešno potvrđena', flush = True)
        print('Hash transakcije:', receipt.transactionHash.hex(), flush = True)
    except Exception as e:
        error_message = str(e)
        print(error_message, flush=True)
        # Determine which require statement caused the error
        if "Order is not paid" in error_message:
            return jsonify(message = 'Transfer not complete.'), 400
        else: return jsonify(message = error_message), 400

    print(contract.functions.getCourierAssigned().call(), flush=True)
    print(contract.functions.getCourier().call(), flush=True)

    order.status = 'PENDING'
    database.session.add(order)
    database.session.commit()

    return make_response('', 200)



if (__name__ == "__main__"):
    application.run(debug = True, host = "0.0.0.0", port=5006)