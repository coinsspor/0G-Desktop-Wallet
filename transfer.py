import httpx
import time
from mospy import Account, Transaction
from cosmospy_protobuf.cosmos.base.v1beta1.coin_pb2 import Coin  # Doğru modülden Coin import ediliyor
from cosmospy_protobuf.cosmos.bank.v1beta1.tx_pb2 import MsgSend  # MsgSend import ediliyor
from tkinter import messagebox

API_URL = "https://og-testnet-api.itrocket.net"
CHAIN_ID = "zgtendermint_16600-2"
HRP = "0g"
client = httpx.Client(verify=False)

def transfer_token(target_wallet, amount, denom, fee, gas, private_key):
    if private_key.startswith("0x"):
        private_key = private_key[2:]
    
    target_wallet = target_wallet.lower()
    
    account = Account(private_key=private_key, hrp=HRP, eth=True)
    account_address = account.address

    def fetch_account_info():
        response = client.get(f"{API_URL}/cosmos/auth/v1beta1/accounts/{account_address}")
        if response.status_code == 200:
            account_data = response.json().get('account', {})
            account.account_number = int(account_data.get('account_number', 0))
            account.next_sequence = int(account_data.get('sequence', 0))
            return True
        else:
            print(f"API'den uygun yanıt alınamadı: {account_address}, Status Code: {response.status_code}")
            print("Response Body:", response.text)
            return False

    if not fetch_account_info():
        return

    tx = Transaction(account=account, gas=int(gas), chain_id=CHAIN_ID)
    tx.set_fee(denom=denom, amount=str(fee))
    
    send_msg = MsgSend(
        from_address=account_address,
        to_address=target_wallet,
        amount=[Coin(amount=str(amount), denom=denom)]
    )
    
    tx.add_raw_msg(send_msg, type_url="/cosmos.bank.v1beta1.MsgSend")
    
    tx_bytes = tx.get_tx_bytes_as_string()
    push_url = f"{API_URL}/cosmos/tx/v1beta1/txs"
    data = {"tx_bytes": tx_bytes, "mode": "BROADCAST_MODE_SYNC"}
    response = client.post(push_url, json=data, headers={'Content-Type': 'application/json'})
    
    response_data = response.json()
    print(response.json())
    
    if response_data['tx_response']['code'] == 0:
        messagebox.showinfo("Transaction successful", "Transaction successful.")
        return True
    else:
        messagebox.showerror("The operation was not successful", f"The operation was not successful: {response_data['tx_response']}")
        return False
