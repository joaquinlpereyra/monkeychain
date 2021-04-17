import click

from monkeychain.blockchain import Blockchain, Block, Tx
from typing import List
from uuid import uuid4
from flask import Flask, request, jsonify

app = Flask(__name__)


NODE_ID = str(uuid4())
BLOCKCHAIN = Blockchain()


@app.route("/add_tx", methods=["POST"])
def add_transaction():
    tx = request.get_json()
    if not tx.get("sender") or not tx.get("receiver") or not tx.get("amount"):
        return "Missing values", 400

    tx = Tx(tx.get("sender"), tx.get("receiver"), tx.get("amount"))

    index = BLOCKCHAIN.new_transaction(tx)
    response = {"index": index}
    return jsonify(response), 201


BLOCKCHAIN.mine()
app.run()
