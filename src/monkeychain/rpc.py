from monkeychain.block import Block
from monkeychain.blockchain import Tx, Block, Blockchain
from flask import Flask
from flask_jsonrpc import JSONRPC
from typing import List

FLASK = Flask(__name__)
jsonrpc = JSONRPC(FLASK, "/api", enable_web_browsable_api=True)


@jsonrpc.method("blockhain.submit_block")
def submit_block(
    self, index: int, timestamp: float, txs: List[dict], proof: int, previous: int
):

    block = Block(
        index,
        timestamp,
        [Tx(tx["sender"], tx["receiver"], tx["amount"]) for tx in txs],
        proof,
        previous,
    )
    if not block.is_valid():
        print("Woops, block is not valid")

    THE_BLOCKCHAIN.append_block(block)
