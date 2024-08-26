# 0G Desktop Wallet



## About the Project

0G Desktop Wallet is a desktop wallet application that interacts with Cosmos and EVM-based networks. With this wallet, you can create new wallets, manage existing ones, transfer tokens, and perform staking operations.

### Features

- **Create a New Wallet:** Creates a new wallet with Ethereum and 0G addresses.
- **Login with an Existing Wallet:** Allows you to log in to an existing wallet using a private key and perform operations.
- **Token Transfer:** You can transfer tokens on EVM and Cosmos (0G) networks.
- **Delegation:** You can perform staking operations by delegating on the Cosmos-based network.
- **Balance Check:** Check your current balance on the Cosmos network.

## Installation

You can start the project by installing the necessary Python packages and running the `main.py` file.

```bash
pip install -r requirements.txt
python main.py
```
# Usage

## Creating a Wallet
When you run `main.py`, click on the **"Create a New Wallet"** button on the main screen to create a new wallet. This will provide you with a private key, Ethereum address, and 0G address.

## Logging into an Existing Wallet
On the main screen, click on the **"Login with Private Key"** button to log in to your wallet using an existing private key.

## Token Transfer
After logging in, you can transfer tokens by entering the target address and amount in the transfer tab.

## Delegation (Staking)
In the **Delegation** tab, you can select a validator and specify an amount to perform staking operations.

# Files

1. **`main.py`**  
   The main entry point of the application. It creates the main window using the Tkinter library and displays the main screen from the `mainscreen.py` file.

2. **`mainscreen.py`**  
   Creates the user interface for the main screen. It allows users to either create a new wallet or log in to an existing one.

3. **`newwallet.py`**  
   Contains the functionality to create a new wallet. It generates an Ethereum private key and a 0G address and displays them to the user.

4. **`login_prvtkey.py`**  
   Allows users to log in with a private key. It derives the Ethereum and 0G addresses from the private key and logs the user in.

5. **`walletaction.py`**  
   Contains the main wallet functions. It includes operations such as transfer, delegation, and balance checking.

6. **`evmtransfer.py`**  
   A module that handles transfer operations on the EVM-based network.

7. **`transfer.py`**  
   Handles transfer operations on the Cosmos-based 0G network.

8. **`delegate.py`**  
   Handles delegation (staking) operations on the Cosmos-based 0G network.

# Requirements
- Python 3.8 or higher

You can install the required Python packages from the `requirements.txt` file.

# License
This project is licensed under the MIT License. For more information, see the [LICENSE](LICENSE) file.
