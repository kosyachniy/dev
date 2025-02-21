# pip install tonsdk requests

import time
import requests

from tonsdk.contract.wallet import Wallets, WalletVersionEnum
from tonsdk.utils import to_nano, b64str_to_bytes

# Replace with your actual toncenter API endpoint and key.
TONCENTER_ENDPOINT = "https://toncenter.com/api/v2"
API_KEY = "6595412441250364d98ee0326ab76c36863491ed850fad6ddddef8f6b9d3bf50"


class TonMainnet:
    """
    Python class to interact with the TON mainnet using toncenter.

    Requires:
      pip install tonsdk requests

    Provide your own toncenter API key in API_KEY.

    Example usage:
        ton = TonMainnet.create_wallet()
        print(ton.mnemonic)
        print("Address", ton.get_address())
        print("Balance", ton.get_balances())
        # sending
        # tx_link = ton.send_ton(to_address, amount_in_ton)
        # info = ton.get_transaction_info(tx_link)
    """

    def __init__(self, mnemonic=None):
        self.mnemonic = mnemonic
        # self.wallet is a Wallets class from tonsdk
        if mnemonic:
            # Use v4r2 (standard multi-seq) wallet, workchain=0
            self.wallet = Wallets.from_mnemonics(
                mnemonic, wallet_version=WalletVersionEnum.v4r2, workchain=0
            )
            # derive user-friendly address
            self.address = self.wallet.address.to_string(
                is_user_friendly=True, url_safe=True
            )
        else:
            self.wallet = None
            self.address = None

    @staticmethod
    def create_wallet():
        """
        Creates a new wallet (mnemonics + internal wallet object) using the standard v4r2.
        Returns:
            TonMainnet: an instance of TonMainnet with newly generated mnemonic.
        """
        new_mnemonic = Wallets.create_mnemonics()
        return TonMainnet(new_mnemonic)

    def get_address(self) -> str:
        """
        Return this wallet's user-friendly TON address.
        """
        return self.address

    def get_balances(self) -> dict:
        """
        Fetch the wallet's balance from toncenter. Returns in TON.

        Returns:
            dict: {"balance": float}
        """
        if not self.address:
            raise ValueError(
                "Wallet not initialized. Provide mnemonic or create a new wallet."
            )

        url = f"{TONCENTER_ENDPOINT}/getAddressInformation"
        params = {"address": self.address}
        headers = {"X-API-Key": API_KEY}
        resp = requests.get(url, params=params, headers=headers).json()
        if resp.get("ok"):
            balance_nano = int(resp["result"].get("balance", 0))
            return {"balance": balance_nano / 10**9}
        else:
            raise Exception(f"Error getting balance: {resp}")

    def _get_seqno(self) -> int:
        """
        Retrieve the current seqno for the wallet from toncenter.
        """
        url = f"{TONCENTER_ENDPOINT}/getWalletInformation"
        params = {"address": self.address}
        headers = {"X-API-Key": API_KEY}
        resp = requests.get(url, params=params, headers=headers).json()
        if resp.get("ok"):
            return resp["result"].get("seqno", 0)
        else:
            raise Exception(f"Failed to get seqno: {resp}")

    def send_ton(self, to_address: str, amount: float, message: str = "") -> str:
        """
        Send TON from this wallet to another address.
        Creates and signs a transfer message, then sends the BOC to toncenter.
        Args:
            to_address (str): Recipient's user-friendly TON address.
            amount (float): Amount of TON to send.
            message (str): Optional payload for the transaction.

        Returns:
            str: A transaction link (tonviewer.com) using the returned transaction hash.
        """
        if not self.wallet:
            raise ValueError(
                "No wallet instance. Provide mnemonic in constructor or use create_wallet()."
            )

        seqno = self._get_seqno()
        # Build transfer message using the TON SDK
        transfer = self.wallet.create_transfer_message(
            to_addr=to_address,
            amount=to_nano(amount, "ton"),
            seqno=seqno,
            payload=message,
        )

        # The returned object is {"message": <Cell>, "sign": <bytes>}
        boc = transfer["message"].to_boc(False)

        # Send BOC via toncenter
        send_url = f"{TONCENTER_ENDPOINT}/sendBoc"
        headers = {"X-API-Key": API_KEY}
        data = {"boc": boc}
        send_resp = requests.post(send_url, json=data, headers=headers).json()
        if send_resp.get("ok"):
            # Extract base64 transaction hash
            tx_hash_b64 = send_resp["result"]["hash"]
            # Build a link for tonviewer
            return f"https://tonviewer.com/transaction/{tx_hash_b64}"
        else:
            raise Exception(f"Transaction failed: {send_resp}")

    def get_transaction_info(self, tx_link: str):
        """
        Retrieve transaction info from toncenter by scanning recent transactions.
        Args:
            tx_link (str): Transaction link from send_ton.
        Returns:
            dict: { 'status': str, 'from_address': str, 'to_address': str, 'amount': float }
                   or not found.
        """
        if not self.address:
            raise ValueError("Wallet not initialized.")

        tx_hash = tx_link.split("/")[-1]
        # We'll fetch the last 10 transactions and look for the one matching tx_hash.
        url = f"{TONCENTER_ENDPOINT}/getTransactions"
        headers = {"X-API-Key": API_KEY}
        params = {"address": self.address, "limit": 10}
        resp = requests.get(url, params=params, headers=headers).json()
        if resp.get("ok"):
            for tx in resp["result"]:
                this_hash = tx.get("transaction_id", {}).get("hash")
                if this_hash == tx_hash:
                    # parse basic info
                    # if utime < now => it's final, else pending (rarely used in TON, but for consistency)
                    status = (
                        "finalized" if tx.get("utime", 0) < time.time() else "pending"
                    )
                    in_msg = tx.get("in_msg", {})
                    out_msgs = tx.get("out_msgs", [])
                    from_address = in_msg.get("source")
                    to_address = in_msg.get("destination")
                    amount = int(in_msg.get("value", 0)) / 10**9

                    # Alternatively check out_msgs to see if this wallet is the source.

                    return {
                        "status": status,
                        "from_address": from_address,
                        "to_address": to_address,
                        "amount": amount,
                    }
            return {
                "status": "not found",
                "from_address": None,
                "to_address": None,
                "amount": 0.0,
            }
        else:
            raise Exception(f"Error fetching transactions: {resp}")


if __name__ == "__main__":
    # 1. Create a new wallet
    wallet = TonMainnet.create_wallet()
    print("Mnemonic:", wallet.mnemonic)
    print("Address:", wallet.get_address())

    # 2. Check balance
    balance = wallet.get_balances()
    print("Balance:", balance)

    # 3. Send TON (make sure wallet is deployed & funded)
    tx_link = wallet.send_ton(
        "EQCexampleDestinationAddress", 0.05, "Hello from Python!"
    )
    print("Transaction link:", tx_link)

    # 4. Get transaction details
    tx_info = wallet.get_transaction_info(tx_link)
    print("Transaction Info:", tx_info)
