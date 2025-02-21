# Grok 3

import asyncio

from ton import TonlibClient, Wallet


class TONWallet:
    def __init__(self, private_key=None):
        """
        Initialize the TONWallet with an optional private key.
        If no private key is provided, a new wallet is created.

        Args:
            private_key (str, optional): A hex-encoded private key.
        """
        self.client = TonlibClient()
        if private_key:
            self.wallet = Wallet.from_private_key(self.client, private_key)
        else:
            self.wallet = Wallet.create(self.client)
        self.private_key = self.wallet.private_key  # Hex-encoded private key
        self.public_key = self.wallet.public_key  # Hex-encoded public key

    @classmethod
    def create_wallet(cls):
        """
        Create a new TON wallet and return a TONWallet object.

        Returns:
            TONWallet: An instance of TONWallet with a newly generated key pair.
        """
        return cls()

    def get_address(self):
        """
        Get the TON address of the wallet.

        Returns:
            str: The TON address (e.g., UQD-wupJmp22cy3_5h0OLdO6PlaUiQOSRqheLpYhSoTmtB3l).
        """
        return self.wallet.address

    async def send_ton(self, destination, amount, comment=""):
        """
        Send TON coins to a specified address.

        Args:
            destination (str): The recipient's TON address.
            amount (float): The amount of TON to send.
            comment (str, optional): A comment to include in the transaction.

        Returns:
            str: A URL to view the transaction (e.g., https://tonviewer.com/transaction/...).
        """
        transfer = {
            "destination": destination,
            "amount": self.client.to_nano(amount),  # Convert TON to nanoTON
            "comment": comment,
        }
        tx = await self.wallet.transfer(**transfer)
        return f"https://tonviewer.com/transaction/{tx['transaction_id']['hash']}"

    async def get_transaction_info(self, tx_hash):
        """
        Get information about a specific transaction.

        Args:
            tx_hash (str): The transaction hash.

        Returns:
            dict: Transaction details including status, from_address, to_address, and amount,
                  or None if the transaction is not found.
        """
        tx = await self.client.get_transaction(tx_hash)
        if tx:
            status = tx["status"]
            from_address = tx["in_msg"]["source"]
            to_address = tx["in_msg"]["destination"]
            amount = self.client.from_nano(
                int(tx["in_msg"]["value"])
            )  # Convert nanoTON to TON
            return {
                "status": status,
                "from_address": from_address,
                "to_address": to_address,
                "amount": amount,
            }
        return None

    async def get_balance(self):
        """
        Get the current balance of the wallet.

        Returns:
            float: The balance in TON.
        """
        balance = await self.wallet.get_balance()
        return self.client.from_nano(balance)  # Convert nanoTON to TON


# Example usage
async def main():
    # Create a new wallet
    new_wallet = TONWallet.create_wallet()
    print(f"Private Key: {new_wallet.private_key}")
    print(f"Public Key: {new_wallet.public_key}")
    print(f"Address: {new_wallet.get_address()}")

    # Initialize with an existing private key
    existing_wallet = TONWallet(
        "ca6476163ae96f64f5d12733ff7b8b38e6919c3426db4cf1fdbb1ebcf4eb123a"
    )
    print(f"Address from existing key: {existing_wallet.get_address()}")

    # Example of sending TON (uncomment and replace with actual values)
    # tx_link = await new_wallet.send_ton(
    #     "UQD-wupJmp22cy3_5h0OLdO6PlaUiQOSRqheLpYhSoTmtB3l",
    #     1.0,
    #     "Test transfer"
    # )
    # print(f"Transaction Link: {tx_link}")

    # Example of getting transaction info (uncomment and replace with actual hash)
    # tx_info = await new_wallet.get_transaction_info(
    #     "e2942791f1ee210244541a100495f9d5f2b0e963f17072108c0dfc04a4cef744"
    # )
    # if tx_info:
    #     print(f"Transaction Status: {tx_info['status']}")
    #     print(f"From: {tx_info['from_address']}")
    #     print(f"To: {tx_info['to_address']}")
    #     print(f"Amount: {tx_info['amount']} TON")

    # Get balance
    balance = await new_wallet.get_balance()
    print(f"Balance: {balance} TON")


if __name__ == "__main__":
    asyncio.run(main())
