import click
import requests
import sys

from monkeychain.blockchain import Blockchain, Block, Tx, Network
from typing import List
from uuid import uuid4
import time
from flask import Flask, request, jsonify

app = Flask(__name__)


NODE_ID = str(uuid4())
NETWORK = Network(f"localhost:{sys.argv[1]}")
BLOCKCHAIN = Blockchain(NETWORK)

@app.route("/add_tx", methods=["POST"])
def add_transaction():
    tx = request.get_json()
    if not tx.get("sender") or not tx.get("receiver") or not tx.get("amount"):
        return "Missing values", 400

    tx = Tx(tx.get("sender"), tx.get("receiver"), tx.get("amount"))

    index = BLOCKCHAIN.new_transaction(tx)
    response = {"index": index, "hash": tx.hash}
    return jsonify(response), 201


@app.route("/add_block", methods=["POST"])
def add_block():
    block_json = request.get_json()
    last_block = BLOCKCHAIN.last_block
    block = Block(
        index=block_json.get('index'),
        timestamp=block_json.get('timestamp'),
        txs=[Tx(tx.get("sender"), tx.get("receiver"), tx.get("amount")) for tx in block_json.get('txs')],
        proof=block_json.get('proof'),
        previous=block_json.get('previous'),
    )
    try:
        print(f"[CONTROLLER] [ADD_BLOCK] New block from the outside, hash {block.short_hash}")
        BLOCKCHAIN.append_block(block)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"index": len(BLOCKCHAIN)}), 200

@app.route("/block", methods=["GET"])
def get_block():
    index = int(request.args.get('index'))
    if len(BLOCKCHAIN) <= index:
        return jsonify({"error": "block does not exist yet"}), 404
        
    return jsonify(BLOCKCHAIN.chain[index].as_dict)

        
@app.route("/add_peer", methods=["POST"])
def add_peer():
    peer = request.get_json()
    if not peer.get("endpoint"):
        raise ValueError("Peer must have an endpoint")

    NETWORK.add_peer(peer.get('endpoint'))
    return "OK", 200



@app.route("/get_peers", methods=["GET"])
def get_peers():
    print("Get peers called")
    return jsonify(NETWORK.peers), 200



BLOCKCHAIN.mine()
if len(sys.argv) == 3:
    NETWORK.add_peer(sys.argv[2], notify_peer=True)

app.run(port=int(sys.argv[1]))
