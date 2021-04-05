from time import time
from typing import Optional
from monkeychain.blockchain import Block, Blockchain


class Miner:
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain
        self.pending_txs = []
        pass

    def add_transaction(self, tx):
        self.pending_txs = self.pending_txs.append(tx)

    def work(self):
        pass

    def _new_block(self, proof) -> Optional[Block]:
        previous_hash = hash(self.blockchain.last_block)

        block = Block(
            index=len(self.blockchain) + 1,
            timestamp=time.time(),
            txs=self.pending_txs,
            proof=proof,
            previous=previous_hash,
        )

        if not self.blockchain.append_block(block):
            return None

        self.pending_txs = []
        return block
