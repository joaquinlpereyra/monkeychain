import click

from monkeychain.blockchain import Blockchain, Block, Tx
from typing import List
from flask import Flask
from flask_jsonrpc import JSONRPC

FLASK = Flask(__name__)
jsonrpc = JSONRPC(FLASK, "/api", enable_web_browsable_api=True)

BLOCKCHAIN = Blockchain()


@jsonrpc.method("submit_block")
def submit_block(
    self, index: int, timestamp: float, txs: List[dict], proof: int, previous: int
) -> bool:
    return True


@jsonrpc.method("get_last_block")
def get_last_block() -> Block:
    return BLOCKCHAIN.last_block()
