import httpx
from cosmospy_protobuf.cosmos.base.v1beta1.coin_pb2 import Coin
from cosmospy_protobuf.cosmos.staking.v1beta1.tx_pb2 import MsgDelegate
from mospy import Transaction, Account
from tkinter import messagebox
import json

def delegate_to_validator(validator_address, amount, gas, fee, delegator_address, private_key):
    API_URL = "https://og-testnet-api.itrocket.net"
    CHAIN_ID = "zgtendermint_16600-2"
    delegator_address = delegator_address.lower()
    validator_address = validator_address.lower()

    print(f"Delegator Address: {delegator_address}")
    print(f"Private Key: {private_key}")
    print(f"Validator Address: {validator_address}")
    print(f"Amount: {amount}")
    print(f"Gas: {gas}")
    print(f"Fee: {fee}")

    if private_key.startswith('0x'):
        private_key = private_key[2:]
        print("Removed '0x' prefix from private key.")

    with httpx.Client(verify=False) as client:
        response = client.get(f"{API_URL}/cosmos/auth/v1beta1/accounts/{delegator_address}")
        print(f"Fetched account details for {delegator_address} with status code {response.status_code}")

        if response.status_code != 200:
            print("Failed to fetch account details:", response.text)
            return "Failed to fetch account details.", False

        account_data = response.json().get('account', {})
        account_number = account_data.get('account_number')
        sequence = account_data.get('sequence')

        if account_number is None or sequence is None:
            print("Account details are incomplete.")
            return "Account details are incomplete.", False

        account = Account(
            private_key=private_key,
            account_number=int(account_number),
            next_sequence=int(sequence),
            eth=True
        )

        print("Account created successfully.")

        tx = Transaction(
            account=account,
            chain_id=CHAIN_ID,
            gas=int(gas)
        )

        dmsg = MsgDelegate(
            delegator_address=delegator_address,
            validator_address=validator_address,
            amount=Coin(amount=str(amount), denom="ua0gi")
        )

        tx.set_fee(
            amount=str(fee),
            denom="ua0gi"
        )

        tx.add_raw_msg(dmsg, type_url="/cosmos.staking.v1beta1.MsgDelegate")
        print("Delegate message added to the transaction.")

        tx_bytes = tx.get_tx_bytes_as_string()
        pushable_tx = {
            "tx_bytes": tx_bytes,
            "mode": "BROADCAST_MODE_SYNC"
        }

        response = client.post(f"{API_URL}/cosmos/tx/v1beta1/txs", data=json.dumps(pushable_tx))
        print(response.json())

        response_data = response.json()  # JSON verisi çekildi

        if response_data['tx_response']['code'] == 0:
             messagebox.showinfo("Transaction successful", "Transaction successful.")
             return True
        else:
             messagebox.showerror("The operation was not successful", f"The operation was not successful: {response_data['tx_response']}")
             return False
