import json
from tonsdk.contract.wallet import WalletVersionEnum, Wallets
from tonsdk.crypto import mnemonic_new
from tonsdk.utils import bytes_to_b64str, to_nano


# 1

# # Create wallet and show keys (convert bytes to hex for JSON serialization)
# wallet_workchain = 0
# wallet_version = WalletVersionEnum.v3r2
# mnemonics = mnemonic_new()

# _mnemonics, pub_key, priv_key, wallet = Wallets.from_mnemonics(
#     mnemonics, wallet_version, wallet_workchain
# )

# print("Mnemonic:", mnemonics)
# print("Public key:", pub_key.hex())
# print("Private key:", priv_key.hex())
# print("Wallet address:", wallet.address.to_string())

# # Save wallet info (keys converted to hex)
# wallet_data = {
#     "mnemonics": mnemonics,
#     "public_key": pub_key.hex(),
#     "private_key": priv_key.hex(),
#     "wallet_version": wallet_version.value,
#     "wallet_workchain": wallet_workchain,
# }

# with open("wallet_keys.json", "w") as f:
#     json.dump(wallet_data, f, indent=4)
# print("Wallet keys saved to wallet_keys.json")


# 2

# from tonsdk.utils import Address

# raw_addr = "0:f73489033c9cb7929c5b62ba69521169cb01d4b2bf7132ab59b1d03a622870e4"
# addr = Address(raw_addr)
# user_friendly = addr.to_string(True, True, True)
# print("User-friendly address:", user_friendly)


# 3 Balance

# from tonsdk.provider import ToncenterClient
# from tonsdk.utils import from_nano

# # Instantiate a client (ensure you have your API key and correct base URL)
# client = ToncenterClient(
#     base_url="https://testnet.toncenter.com/api/v2/", api_key="your_api_key_here"
# )

# # Use your wallet address (user-friendly format)
# wallet_address = "UQD-wupJmp22cy3_5h0OLdO6PlaUiQOSRqheLpYhSoTmtB3l"

# # Get wallet info (this method converts nanoTON to TON)
# addr_info = client.get_address_information(wallet_address)
# balance = addr_info.get("balance")  # Already converted from nanoTON

# print("Wallet balance:", balance, "TON")


# 4 Transaction

# import asyncio
# from tonsdk.provider import ToncenterClient, prepare_address, address_state


# async def get_transaction_info(wallet_address):
#     # Initialize the ToncenterClient with your API key
#     client = ToncenterClient(
#         base_url="https://testnet.toncenter.com/api/v2/", api_key="your_api_key_here"
#     )

#     # Prepare the wallet address
#     address = prepare_address(wallet_address)

#     # Fetch the account state
#     account_state = await client.raw_get_account_state(address)

#     # Process the account state to extract transaction information
#     # (This is a simplified example; actual implementation may vary)
#     transactions = account_state.get("transactions", [])

#     for tx in transactions:
#         print(f"Transaction ID: {tx['id']}")
#         print(f"Sender: {tx['sender']}")
#         print(f"Receiver: {tx['receiver']}")
#         print(f"Amount: {tx['amount']} TON")
#         print(f"Timestamp: {tx['timestamp']}")
#         print("-" * 40)

#     # Close the client connection
#     await client.close()


# # Replace with the wallet address you want to query
# wallet_address = "UQD-wupJmp22cy3_5h0OLdO6PlaUiQOSRqheLpYhSoTmtB3l"

# # Run the asynchronous function
# asyncio.run(get_transaction_info(wallet_address))


# 5.1

# # ---- Later: Recover the wallet from the saved file ----
# with open("wallet_keys.json", "r") as f:
#     saved_data = json.load(f)

# recovered_mnemonics = saved_data["mnemonics"]
# recovered_wallet_version = WalletVersionEnum(saved_data["wallet_version"])
# recovered_wallet_workchain = saved_data["wallet_workchain"]

# # Recover wallet using mnemonics (keys are re-derived)
# _recovered_mnemonics, recovered_pub_key, recovered_priv_key, recovered_wallet = (
#     Wallets.from_mnemonics(
#         recovered_mnemonics, recovered_wallet_version, recovered_wallet_workchain
#     )
# )

# print("Recovered wallet address:", recovered_wallet.address.to_string())

# # Create a transfer message to withdraw TON coins
# destination_address = "0:DESTINATION_ADDRESS"  # Replace with actual destination
# amount = to_nano(1, "ton")  # Amount to withdraw
# seqno = 0  # Update with the actual seqno

# transfer_query = recovered_wallet.create_transfer_message(
#     destination_address, amount, seqno
# )
# transfer_boc = bytes_to_b64str(transfer_query["message"].to_boc(False))
# print("Transfer message (Base64 BOC):", transfer_boc)


# 5.2

from tonsdk.contract.wallet import WalletVersionEnum, Wallets
from tonsdk.crypto import mnemonic_new
from tonsdk.utils import to_nano, bytes_to_b64str


with open("wallet_keys.json", "r") as f:
    saved_data = json.load(f)

recovered_mnemonics = saved_data["mnemonics"]
recovered_wallet_version = WalletVersionEnum(saved_data["wallet_version"])
recovered_wallet_workchain = saved_data["wallet_workchain"]

_recovered_mnemonics, recovered_pub_key, recovered_priv_key, recovered_wallet = (
    Wallets.from_mnemonics(
        recovered_mnemonics, recovered_wallet_version, recovered_wallet_workchain
    )
)

print("Recovered wallet address:", recovered_wallet.address.to_string())
wallet = recovered_wallet


# # import asyncio


# # async def main():
# #     seqno = await wallet.methods.seqno().call()
# #     print(f"seqno: {seqno}")


# # asyncio.run(main())


# # # Create or load your sender wallet
# # wallet_workchain = 0
# # wallet_version = WalletVersionEnum.v3r2
# # mnemonics = mnemonic_new()  # or load your existing mnemonics
# # _, pub_key, priv_key, wallet = Wallets.from_mnemonics(
# #     mnemonics, wallet_version, wallet_workchain
# # )

# # # Set the destination address (your current wallet address)
# destination_address = "UQD-wupJmp22cy3_5h0OLdO6PlaUiQOSRqheLpYhSoTmtB3l"

# # Define the amount to send (for example, 1 TON)
# amount = to_nano(0.5, "ton")

# # You need the current wallet seqno (typically fetched from-chain)
# seqno = 0  # <-- Replace with the actual seqno from your wallet state

# # Create the transfer message
# transfer = wallet.create_transfer_message(destination_address, amount, seqno)
# boc = transfer["message"].to_boc(False)

# # (Optional) Print the Base64 BOC of the message
# print("Transfer message (B64):", bytes_to_b64str(boc))


# 6
# from tonsdk.utils import from_b64str, to_b64str
# from tonsdk.boc import BOC

# Your BoC string
boc_str = "te6cckECBAEAAUcAA+GIAe5pEgZ5OW8lOLbFdNKkItOWA6llfuJlVrNjoHTEUOHIEZ433HZsj4GUDCnk4y321k2fv1JXQyJ3FEQh7a/cJV455WkUIy0l5JnNztDpvC0ruoWs/eaGO7QCT2Llcyuw34AlNTRi/////+AAAAAAcAECAwDe/wAg3SCCAUyXuiGCATOcurGfcbDtRNDTH9MfMdcL/+ME4KTyYIMI1xgg0x/TH9Mf+CMTu/Jj7UTQ0x/TH9P/0VEyuvKhUUS68qIE+QFUEFX5EPKj+ACTINdKltMH1AL7AOjRAaTIyx/LH8v/ye1UAFAAAAAAKamjF2YPhueAs7MvK/s1mtf1hmHfLggjfrr5et+4MZGWvphaAGhCAH9hdSTNTts5lv/zDocW6d0fK0pEgckjVC8XSxClQnNaIO5rKAAAAAAAAAAAAAAAAAAAPoTmFA=="

# # Decode the BoC
# boc = BOC(from_b64str(boc_str))

# # Extract the transaction hash
# tx_hash = boc.hash()
# tx_hash_b64 = to_b64str(tx_hash)
# print(f"Transaction Hash (Base64): {tx_hash_b64}")


# import base64

# # Decode Base64 string
# boc_bytes = base64.b64decode(boc_str)

# # Encode bytes to Base64 URL-safe string
# boc_b64url = base64.urlsafe_b64encode(boc_bytes).rstrip(b"=").decode("utf-8")
# print(f"BoC (Base64 URL-safe): {boc_b64url}")


# import base64
# from tonsdk.boc import BOC

# # Your BoC string
# boc_str = "te6cckEBAwEA4QAC44gBZUPZ6qi8Dtmm1cot1P175lXUARlUVwlfMM19lkERK1oCUB3RqDxAFnPpeo191X/jiimn9Bwnq3zwcU/MMjHRNN5sC5tyymBV3SJ1rjyyscAjrDDFAIV/iE+WBySEPP9wCU1NGLsfcvVgAAACSAAYHAECAGhCAFlQ9nqqLwO2abVyi3U/XvmVdQBGVRXCV8wzX2WQRErWoAmJaAAAAAAAAAAAAAAAAAAAAGZCAFlQ9nqqLwO2abVyi3U/XvmVdQBGVRXCV8wzX2WQRErWnMS0AAAAAAAAAAAAAAAAAAADkk4U"

# # Decode the BoC
# boc = BOC.from_b64str(boc_str)

# # Extract the transaction hash
# tx_hash = boc.hash()

# # Convert the hash to Base64 URL encoding
# tx_hash_b64 = base64.urlsafe_b64encode(tx_hash).rstrip(b"=").decode("utf-8")

# # Construct the Tonviewer URL
# tonviewer_url = f"https://tonviewer.com/transaction/{tx_hash_b64}"

# print(f"Transaction Link: {tonviewer_url}")


import base64

# # Your BoC string
# boc_str = "te6cckEBAwEA4QAC44gBZUPZ6qi8Dtmm1cot1P175lXUARlUVwlfMM19lkERK1oCUB3RqDxAFnPpeo191X/jiimn9Bwnq3zwcU/MMjHRNN5sC5tyymBV3SJ1rjyyscAjrDDFAIV/iE+WBySEPP9wCU1NGLsfcvVgAAACSAAYHAECAGhCAFlQ9nqqLwO2abVyi3U/XvmVdQBGVRXCV8wzX2WQRErWoAmJaAAAAAAAAAAAAAAAAAAAAGZCAFlQ9nqqLwO2abVyi3U/XvmVdQBGVRXCV8wzX2WQRErWnMS0AAAAAAAAAAAAAAAAAAADkk4U"

# # Decode the BoC
# boc_bytes = base64.b64decode(boc_str)

# # Extract the transaction hash (first 32 bytes)
# tx_hash = boc_bytes[:32]

# # Convert the hash to Base64 URL encoding
# tx_hash_b64 = base64.urlsafe_b64encode(tx_hash).rstrip(b"=").decode("utf-8")

# # Construct the Tonviewer URL
# tonviewer_url = f"https://tonviewer.com/transaction/{tx_hash_b64}"

# print(f"Transaction Link: {tonviewer_url}")


# import base64

# # Your BoC string
# boc_str = "te6cckEBAwEA4QAC44gBZUPZ6qi8Dtmm1cot1P175lXUARlUVwlfMM19lkERK1oCUB3RqDxAFnPpeo191X/jiimn9Bwnq3zwcU/MMjHRNN5sC5tyymBV3SJ1rjyyscAjrDDFAIV/iE+WBySEPP9wCU1NGLsfcvVgAAACSAAYHAECAGhCAFlQ9nqqLwO2abVyi3U/XvmVdQBGVRXCV8wzX2WQRErWoAmJaAAAAAAAAAAAAAAAAAAAAGZCAFlQ9nqqLwO2abVyi3U/XvmVdQBGVRXCV8wzX2WQRErWnMS0AAAAAAAAAAAAAAAAAAADkk4U"

# # Decode the BoC
# boc_bytes = base64.b64decode(boc_str)

# # Extract the transaction hash (first 32 bytes)
# tx_hash = boc_bytes[:32]

# # Convert the hash to Base64 URL encoding
# tx_hash_b64 = base64.urlsafe_b64encode(tx_hash).rstrip(b"=").decode("utf-8")

# # Construct the Tonviewer URL
# tonviewer_url = f"https://tonviewer.com/transaction/{tx_hash_b64}"

# print(f"Transaction Link: {tonviewer_url}")


# import base64

# # Your BoC string
# boc_str = "te6cckEBAwEA4QAC44gBZUPZ6qi8Dtmm1cot1P175lXUARlUVwlfMM19lkERK1oCUB3RqDxAFnPpeo191X/jiimn9Bwnq3zwcU/MMjHRNN5sC5tyymBV3SJ1rjyyscAjrDDFAIV/iE+WBySEPP9wCU1NGLsfcvVgAAACSAAYHAECAGhCAFlQ9nqqLwO2abVyi3U/XvmVdQBGVRXCV8wzX2WQRErWoAmJaAAAAAAAAAAAAAAAAAAAAGZCAFlQ9nqqLwO2abVyi3U/XvmVdQBGVRXCV8wzX2WQRErWnMS0AAAAAAAAAAAAAAAAAAADkk4U"

# # Decode the BoC
# boc_bytes = base64.b64decode(boc_str)

# # Extract the transaction hash (first 32 bytes)
# tx_hash = boc_bytes[:32]

# # Convert the hash to Base64 URL encoding
# tx_hash_b64 = base64.urlsafe_b64encode(tx_hash).rstrip(b"=").decode("utf-8")

# # Construct the Tonviewer URL
# tonviewer_url = f"https://tonviewer.com/transaction/{tx_hash_b64}"

# print(f"Transaction Link: {tonviewer_url}")
