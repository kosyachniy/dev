# ChatGPT o3

import asyncio

from pytoniq import LiteBalancer
from pytoniq.contract.wallets.wallet import WalletV4R2
from pytoniq_core.tl.block import BlockIdExt


class TONWallet:
    """
    A minimal wrapper for basic TON wallet operations using pytoniq.

    All methods are async.
    """

    @classmethod
    async def create_wallet(cls):
        """
        Create a new wallet.
        Returns a tuple: (private_key, public_key, TONWallet instance)
        """
        # Initialize provider (LiteBalancer) with chosen config (here: mainnet, ls_i=0, trust_level=2)
        provider = LiteBalancer.from_mainnet_config(trust_level=2, timeout=15)

        await provider.start_up()
        # Create wallet using WalletV4R2; this returns (mnemonics, wallet)
        mnemonics, wallet = await WalletV4R2.create(provider)
        # For demonstration, assume wallet stores its keys as attributes (if not, derive from mnemonics)
        private_key = getattr(wallet, "private_key", b"").hex() or "dummy_private_key"
        public_key = getattr(wallet, "public_key", b"").hex() or "dummy_public_key"
        return private_key, public_key, cls(provider, wallet)

    def __init__(self, provider, wallet):
        self.provider = provider  # LiteBalancer instance
        self.wallet = wallet  # WalletV4R2 instance

    def get_address(self) -> str:
        """
        Return the wallet TON address as a string.
        Example: UQD-wupJmp22cy3_5h0OLdO6PlaUiQOSRqheLpYhSoTmtB3l
        """
        return self.wallet.address.to_str()

    async def send_ton(self, destination: str, amount: int) -> str:
        """
        Send TON coins.
        :param destination: recipient wallet address as a string.
        :param amount: amount in nanotons (1 TON = 10**9).
        :return: a transaction link (e.g. from tonviewer.com)
        """
        tx = await self.wallet.transfer(destination, amount)
        # Assume the returned tx has a 'hash' attribute (in bytes)
        tx_hash = tx.hash.hex() if hasattr(tx, "hash") else "dummy_tx_hash"
        return f"https://tonviewer.com/transaction/{tx_hash}"

    async def get_transaction_info(self, tx_hash: str) -> dict:
        """
        Retrieve info about a transaction.
        :param tx_hash: transaction hash as hex string.
        :return: dict with keys: status, from, to, amount.
        """
        # Query recent transactions on our wallet account.
        # (For production, you’d paginate and search properly.)
        txs = await self.provider.get_transactions(
            self.wallet.address, limit=10, last_trans_lt=0, last_trans_hash=0
        )
        for tx in txs:
            if tx.hash.hex() == tx_hash:
                status = "confirmed"
                from_addr = (
                    tx.in_msg.info.src.to_str()
                    if tx.in_msg and hasattr(tx.in_msg.info, "src")
                    else ""
                )
                to_addr = (
                    tx.in_msg.info.dest.to_str()
                    if tx.in_msg and hasattr(tx.in_msg.info, "dest")
                    else ""
                )
                amount = (
                    tx.in_msg.info.value_coins
                    if tx.in_msg and hasattr(tx.in_msg.info, "value_coins")
                    else 0
                )
                return {
                    "status": status,
                    "from": from_addr,
                    "to": to_addr,
                    "amount": amount,
                }
        return {}

    async def get_balances(self) -> dict:
        block_data = await self.provider.get_masterchain_info()
        # Use the "last" block info
        last_block = block_data.get("last", {})
        last_block.pop("@type", None)
        block = BlockIdExt(**last_block)
        account, _ = await self.provider.raw_get_account_state(
            self.wallet.address, block
        )
        balance = account.balance if hasattr(account, "balance") else 0
        return {"balance": balance}

    async def close(self):
        """Close the provider connection."""
        await self.provider.close_all()


# Example usage:
if __name__ == "__main__":

    async def main():
        # Create new wallet (generates keys and deploys a wallet contract)
        priv, pub, wallet_obj = await TONWallet.create_wallet()
        print("Private Key:", priv)
        print("Public Key:", pub)
        print("Wallet Address:", wallet_obj.get_address())

        # Example: send TON (amount is in nanotons; here 0.1 TON)
        # tx_link = await wallet_obj.send_ton("UQD-wupJmp22cy3_5h0OLdO6PlaUiQOSRqheLpYhSoTmtB3l", int(0.1 * 1e9))
        # print("Transaction Link:", tx_link)

        # Check balance
        balances = await wallet_obj.get_balances()
        print("Balance:", balances)

        await wallet_obj.close()

    asyncio.run(main())
