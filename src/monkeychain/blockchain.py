import hashlib
import json
from time import time
from typing import Optional
from monkeychain.block import Block
from typing import List
from dataclasses import dataclass


class Tx:
    def __init__(self, sender: int, receiver: int, amount: int):
        self._sender = sender
        self._receiver = receiver
        self._amount = amount

        self.as_dict = {
            "sender": self._sender,
            "receiver": self._receiver,
            "amount": self._amount,
        }
        self.as_json = json.dumps(self.as_dict, sort_keys=True).encode()
        self.hash = hashlib.sha256(self.as_json).hexdigest


class Block:
    def __init__(self, index, timestamp, txs, proof, previous):
        self._index = index
        self._timestamp = timestamp
        self._txs = txs
        self._proof = proof
        self._previous = previous

        self.as_dict = {
            "index": self._index,
            "timestamp": self._timestamp,
            "txs": self._txs,
            "proof": self._proof,
            "previous": self._previous,
        }
        self.as_json = json.dumps(self.as_dict, sort_keys=True).encode()
        self.hash = hashlib.sha256(self.as_json).hexdigest

    def __hash__(self):
        return self.hash


class Blockchain:
    def __init__(self):
        """Create a new blockchain. If you are not a monkey this
        will make your computer explode.
        """
        self.chain = []

    def __len__(self):
        return len(self.chain)

    def append_block(self, block):
        """Creates a new block and adds it to the chain"""
        self.chain.append(block)
        return block

    def last_block(self) -> Optional[Block]:
        """Return the last block on the chain"""
        return self.chain[-1]
