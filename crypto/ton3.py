# DeepSeek

import os
import asyncio
import requests

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pytoniq import WalletV4R2, LiteBalancer, begin_cell


class TONWallet:
    def __init__(self, private_key=None):
        if private_key is not None:
            private_key_bytes = bytes.fromhex(private_key)
            if len(private_key_bytes) != 64:
                raise ValueError("Invalid private key length (must be 64 bytes)")
            self.seed = private_key_bytes[:32]
            self.public_key = private_key_bytes[32:]
            self._validate_key_pair()
        else:
            self.seed = os.urandom(32)
            private_key = Ed25519PrivateKey.from_private_bytes(self.seed)
            self.public_key = private_key.public_key().public_bytes_raw()

        self.private_key_hex = (self.seed + self.public_key).hex()
        self.wallet = WalletV4R2(public_key=self.public_key)
        self.address = self.wallet.address

    def _validate_key_pair(self):
        private_key = Ed25519PrivateKey.from_private_bytes(self.seed)
        derived_public = private_key.public_key().public_bytes_raw()
        if derived_public != self.public_key:
            raise ValueError("Public key doesn't match private key seed")

    @classmethod
    def create_wallet(cls):
        """Create new wallet and return instance"""
        return cls()

    def get_address(self):
        """Get TON address in user-friendly format"""
        return self.address.to_str()

    def send_ton(self, to_address: str, amount: float):
        """Send TON to another address"""

        async def _send():
            async with LiteBalancer.from_mainnet_config() as client:
                await self.wallet.init(client)
                transfer = self.wallet.transfer(
                    destination=to_address,
                    amount=int(amount * 1e9),
                    body=begin_cell().end_cell(),
                )
                await transfer.send()
                return f"https://tonviewer.com/transaction/{transfer.hash.hex()}"

        return asyncio.run(_send())

    def get_balance(self):
        """Get current balance in TON"""
        url = "https://toncenter.com/api/v2/getAddressInformation"
        response = requests.get(url, params={"address": self.get_address()})
        return int(response.json()["result"]["balance"]) / 1e9

    @staticmethod
    def get_transaction_info(tx_hash: str):
        """Get transaction details"""
        url = f"https://toncenter.com/api/v2/getTransaction/{tx_hash}"
        response = requests.get(url)
        data = response.json()["result"]
        return {
            "status": "success" if data["success"] else "failed",
            "from": data["in_msg"]["source"],
            "to": data["in_msg"]["destination"],
            "amount": int(data["in_msg"]["value"]) / 1e9,
        }


# Example usage
if __name__ == "__main__":
    # Create new wallet
    wallet = TONWallet.create_wallet()
    print(f"Private Key: {wallet.private_key_hex}")
    print(f"Address: {wallet.get_address()}")

    # Initialize with existing key
    existing_wallet = TONWallet(
        private_key="ca6476163ae96f64f5d12733ff7b8b38e6919c3426db4cf1fdbb1ebcf4eb123a660f86e781c3b32f2bfb359ad7f58661df2e08237ebaf97adfb8319196be985a"
    )
    print(f"Existing wallet balance: {existing_wallet.get_balance()} TON")
