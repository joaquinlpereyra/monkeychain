import hashlib
import json
from typing import List
import threading
import requests
import time
import random


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
        self.txs = txs
        self.proof = proof
        self.previous = previous

        self.as_dict = {
            "index": self.index,
            "timestamp": self._timestamp,
            "txs": [tx.as_dict for tx in self.txs],
            "proof": self.proof,
            "previous": self.previous,
        }
        self.as_json = json.dumps(self.as_dict, sort_keys=True).encode()
        self.hash = hashlib.sha256(self.as_json).hexdigest()
        self.short_hash = self.hash[:8]

    def __hash__(self):
        return self.hash


class Network:
    def __init__(self, local_endpoint):
        print(f"[NETWORK] Local endpoint: {local_endpoint}")
        self.peers = []
        self.local_endpoint = local_endpoint

    def add_peer(self, peer, notify_peer=False):
        print(f"[NETWORK] Trying to add peer: {peer}")

        if peer not in self.peers:
            print(f"[NETWORK] Adding peer: {peer}")
            self.peers.append(f"http://{peer}")
            if notify_peer:
                requests.post(f"http://{peer}/add_peer", json={'endpoint': f"{self.local_endpoint}"})

        print(f"[NETWORK] Peer list: {self.peers}")

    def broadcast_block(self, block):
        for peer in self.peers:
            print(f"[NETWORK] [BROADCAST BLOCK] Hash {block.short_hash} to peer {peer}")
            requests.post(f"{peer}/add_block", json=block.as_dict)
                

class Blockchain:
    GENESIS = Block(0, 0.00, [], 100, 0)

    def __init__(self, network):
        """Create a new blockchain. If you are not a monkey this
        will make your computer explode.
        """
        self.chain: List[Block] = [Blockchain.GENESIS]
        self.pending_transactions: List[Tx] = []
        self.network = network

    def new_transaction(self, tx: Tx):
        print(f"Adding unconfirmed transaction: {tx.hash} -> {tx.as_dict}")
        self.pending_transactions.append(tx)
        return self.last_block.index + 1

    def mine(self):
        def do():
            while True:
                time.sleep(random.uniform(10, 5))
                proof = 0
                last_proof = self.last_block.proof
                while not self.is_valid_proof(last_proof, proof):
                    # Check again for the last proof, as another node
                    # in the network may have sent us a valid block
                    last_proof = self.last_block.proof
                    proof += 1
                block = Block(
                    index=self.last_block.index + 1,
                    timestamp=time.time(),
                    txs=self.pending_transactions,
                    proof=proof,
                    previous=self.last_block.hash,
                )
                print(f"[BLOCKCHAIN] [MINE] New block! hash {block.short_hash}, proof {proof}!")
                self.append_block(block)
                self.network.broadcast_block(block)
                self.pending_transactions = []

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

    def append_block(self, block) -> Block:
        """Creates a new block and adds it to the chain"""
        print(f"[BLOCKCHAIN] [APPEND_BLOCK] Index: {block.index} | proof {block.proof} | hash {block.short_hash}")

        if not self.is_valid_proof(self.last_block.proof, block.proof):
            print(f"[BLOCKCHAIN] [APPEND_BLOCK] Index: {block.index} | proof {block.proof} invalid!")
            raise ValueError("Invalid proof on block")

        if block.index == self.last_block.index:
            print(f"[BLOCKCHAIN] [APPEND_BLOCK] Index: {block.index} | Received just computed block. FIGHT!")
            raise ValueError("Already have that block.")

        if block.previous != self.last_block.hash:
            print(f"[BLOCKCHAIN] [APPEND_BLOCK] Index: {block.index} | Different previous block!")
            if block.index <= self.last_block.index:
                print(f"[BLOCKCHAIN] [APPEND_BLOCK] Index: {block.index} | Received block is behind.")
                raise ValueError("Stale block received")

        print(f"[BLOCKCHAIN] [APPEND_BLOCK] Accepted block hash: {block.short_hash} | txs: {[tx.hash for tx in block.txs]}")
        

        self.chain.append(block)
        return block

    @property
    def last_block(self) -> Block:
        """Return the last block on the chain"""
        return self.chain[-1]
