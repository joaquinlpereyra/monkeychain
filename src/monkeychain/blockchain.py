import hashlib
import json
from time import time
from typing import List
import threading
import time


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
        self.hash = hashlib.sha256(self.as_json).hexdigest()

    def __hash__(self):
        return self.hash


class Block:
    def __init__(self, index, timestamp, txs, proof, previous):
        self.index = index
        self._timestamp = timestamp
        self._txs = txs
        self.proof = proof
        self._previous = previous

        self.as_dict = {
            "index": self.index,
            "timestamp": self._timestamp,
            "txs": [tx.as_dict for tx in self._txs],
            "proof": self.proof,
            "previous": self._previous,
        }
        self.as_json = json.dumps(self.as_dict, sort_keys=True).encode()
        self.hash = hashlib.sha256(self.as_json).hexdigest()

    def __hash__(self):
        return self.hash


class Blockchain:
    GENESIS = Block(0, 0.00, [], 100, 0)

    def __init__(self):
        """Create a new blockchain. If you are not a monkey this
        will make your computer explode.
        """
        self.chain: List[Block] = [Blockchain.GENESIS]
        self.pending_transactions: List[Tx] = []

    def new_transaction(self, tx: Tx):
        print(f"Adding unconfirmed transaction: {tx.hash} -> {tx.as_dict}")
        self.pending_transactions.append(tx)
        return self.last_block.index + 1

    def mine(self):
        def do():
            while True:
                proof = 0
                last_proof = self.last_block.proof
                while not self.is_valid_proof(last_proof, proof):
                    # Check again for the last proof, as another node
                    # in the network may have sent us a valid block
                    last_proof = self.last_block.proof
                    proof += 1
                print(f"Found block with proof {proof}! Adding and propagating.")
                self._append_block(proof)

        thread = threading.Thread(target=do)
        thread.start()

    def is_valid_proof(self, last_proof, proof):
        # Check out how this is literally a blockchain
        # The consensus algorithm has as a rule that in order to be valid
        # SHA of the proof of the previos block and the current proposed proof
        # has to start with four zeroes, thus CHAINING the blocks together.
        #
        # If I were to modify the proof of an old block in the blockchain,
        # inmediatly all future # proofs would become invalid as well.
        return (
            hashlib.sha256(f"{last_proof}{proof}".encode()).hexdigest()[:5] == "0" * 5
        )

    def __len__(self):
        return len(self.chain)

    def _append_block(self, proof) -> Block:
        """Creates a new block and adds it to the chain"""
        print(f"New block: index {self.last_block.index + 1} | proof {proof}")
        block = Block(
            index=self.last_block.index + 1,
            timestamp=time.time(),
            txs=self.pending_transactions,
            proof=proof,
            previous=self.last_block.hash,
        )
        self.chain.append(block)
        self.pending_transactions = []
        return block

    @property
    def last_block(self) -> Block:
        """Return the last block on the chain"""
        return self.chain[-1]
