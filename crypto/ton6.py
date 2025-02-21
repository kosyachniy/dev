import tonclient


class TonWallet:
    def __init__(self, private_key=None):
        self.client = tonclient.TonClient()
        self.client.init_client()
        if private_key:
            self.private_key = private_key
            self.public_key = self.get_public_key(private_key)
        else:
            self.private_key, self.public_key = self.create_wallet()

    def create_wallet(self):
        result = self.client.crypto.generate_random_sign_keys()
        return result.private, result.public

    def get_public_key(self, private_key):
        result = self.client.crypto.public_key_from_private_key(private_key)
        return result.public_key

    def get_address(self):
        result = self.client.crypto.address_from_public_key(self.public_key)
        return result.address

    def send_ton(self, to_address, amount):
        params = tonclient.TonSendParameters(
            address=to_address,
            amount=amount * 1e9,  # Convert to nanotokens
            send_mode=tonclient.SendMode.PAY_GAS_SEPARATELY,
        )
        result = self.client.send_transfer(params, private_key=self.private_key)
        return result.transaction.info.transaction_id

    def get_transaction_info(self, tx_id):
        tx_info = self.client.get_transaction_info(tx_id)
        return {
            "status": tx_info.transaction.status_name,
            "from_address": tx_info.transaction.in_msg_descr.src,
            "to_address": tx_info.transaction.out_msgs[0].dst,
            "amount": tx_info.transaction.out_msgs[0].value
            / 1e9,  # Convert from nanotokens
        }

    def get_balances(self):
        account_info = self.client.get_account_info(self.get_address())
        return account_info.balance / 1e9  # Convert from nanotokens


if __name__ == "__main__":
    wallet = TonWallet()
    print("Private Key:", wallet.private_key)
    print("Public Key:", wallet.public_key)
    print("Address:", wallet.get_address())

    to_address = "EQD_WJW6RB8sHYHOAxZdFaYmzDLJEYVFnkY9Gg_Zt_Ue_Uc_"
    amount = 0.01
    tx_id = wallet.send_ton(to_address, amount)
    print("Transaction ID:", tx_id)

    tx_info = wallet.get_transaction_info(tx_id)
    print("Transaction Info:", tx_info)

    balance = wallet.get_balances()
    print("Balance:", balance)
