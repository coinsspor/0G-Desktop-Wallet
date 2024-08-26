import time
import tkinter as tk
import requests
from tkinter import ttk, messagebox
import mainscreen  # Ana ekran modülü
from delegate import delegate_to_validator  # delegate.py'den fonksiyonu import et
from transfer import transfer_token  # transfer.py'den transfer_token fonksiyonunu import et
from evmtransfer import evm_transfer  # evmtransfer.py'den evm_transfer fonksiyonunu import et
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

valid_adr = None


def clear_content(root):
    for widget in root.winfo_children():
        widget.destroy()

def copy_to_clipboard(root, content):
    root.clipboard_clear()
    root.clipboard_append(content)
    root.update()
    messagebox.showinfo("Copy Success", f"{content} Copied!")

def fetch_balances(address):
    url = f"https://og-testnet-api.itrocket.net/cosmos/bank/v1beta1/balances/{address}"
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        data = response.json()
        return data.get('balances', [])
    else:
        print("Failed to fetch balances:", response.status_code)
        return []

def fetch_validators():
    url = "https://og-testnet-api.itrocket.net/cosmos/staking/v1beta1/validators?pagination.limit=300&status=BOND_STATUS_BONDED"
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        validators = response.json().get('validators', [])
        return [(v['description']['moniker'] + ' (' + f"{float(v['commission']['commission_rates']['rate']) * 100:.1f}%)", v['operator_address']) for v in validators]
    else:
        print("Failed to fetch validators:", response.status_code)
        return []

def format_balance(amount):
    # İlk olarak string'i float'a çevir, sonra sonucu formatla
    return f"{float(amount) / 10**6:.6f}"

def update_max_amount(entry, oG_address, root):
    current_balances = fetch_balances(oG_address)  # Her seferinde güncel bakiyeleri çek
    total_balance_wei = sum(int(balance['amount']) for balance in current_balances if balance['denom'] == 'ua0gi')
    total_balance_ua0gi = total_balance_wei / 1e6
    max_transferable_ua0gi = max(0, total_balance_ua0gi - 0.01)

    entry.delete(0, tk.END)
    if max_transferable_ua0gi > 0:
        entry.insert(0, f"{max_transferable_ua0gi:.6f}")
    else:
        entry.insert(0, "0.000000")
        messagebox.showinfo("Insufficient Balance", "You need at least 0.01 ua0gi more in your wallet to perform transactions.", parent=root)


def update_balance(balance_label, address):
    balances = fetch_balances(address)
    if balances:
        balance_str = " ".join([f"{format_balance(balance['amount'])} {balance['denom']}" for balance in balances])
        balance_label.config(text=f"Balances: {balance_str}")
    else:
        balance_label.config(text="Balances: 0")

def perform_transfer(entry, target_address_entry, fee_entry, gas_entry, oG_address, private_key, root,balance_label):
    try:
        amount_ua0gi = float(entry.get())  # Kullanıcıdan alınan miktarı ua0gi cinsinden al
        amount_wei = int(amount_ua0gi * 10**6)  # Wei'ye çevir
    except ValueError:
        messagebox.showerror("Error", "Invalid amount entered. Please enter a numeric value.", parent=root)
        return

    current_balances = fetch_balances(oG_address)  # Güncel bakiyeleri çek
    total_balance_wei = sum(int(balance['amount']) for balance in current_balances if balance['denom'] == 'ua0gi')

    if amount_wei > total_balance_wei:
        messagebox.showwarning("Warning", "Insufficient funds for this transaction.", parent=root)
        return

    if total_balance_wei - amount_wei < 0.01 * 10**6:
        messagebox.showwarning("Warning", "Insufficient balance after transfer. Minimum balance of 0.01 ua0gi required.", parent=root)
        return

    # Tüm kontroller geçilirse, transfer işlemini doğru sıra ile parametreleri vererek gerçekleştir
    success = transfer_token(target_address_entry.get(), str(amount_wei), 'ua0gi', fee_entry.get(), gas_entry.get(), private_key)
    print("sonuc",success)
    if success==True:
        time.sleep(5)
        update_balance(balance_label, oG_address)


def perform_delegate(valid_adr, entry, gas_entry, fee_entry, oG_address, private_key, root,balance_label):
    try:
        amount_ua0gi = float(entry.get())  # Kullanıcıdan alınan miktarı ua0gi cinsinden al
        amount_wei = int(amount_ua0gi * 10**6)  # Wei'ye çevir
    except ValueError:
        messagebox.showerror("Error", "Invalid amount entered. Please enter a numeric value.", parent=root)
        return

    current_balances = fetch_balances(oG_address)  # Güncel bakiyeleri çek
    total_balance_wei = sum(int(balance['amount']) for balance in current_balances if balance['denom']== 'ua0gi')

    if amount_wei > total_balance_wei:
        messagebox.showwarning("Warning", "Insufficient funds for this transaction.", parent=root)
        return

    if total_balance_wei - amount_wei < 0.01 * 10**6:
        messagebox.showwarning("Warning", "Insufficient balance after transfer. Minimum balance of 0.01 ua0gi required.", parent=root)
        return

    # Tüm kontroller geçilirse, transfer işlemini doğru sıra ile parametreleri vererek gerçekleştir
    success = delegate_to_validator(valid_adr, str(amount_wei), gas_entry.get(),fee_entry.get(),oG_address,private_key)
    print("sonuc",success)
    if success==True:
        time.sleep(5)
        update_balance(balance_label, oG_address)

def wallet_actions(root, evm_address, oG_address, private_key):
    clear_content(root)
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TFrame', background='#FFE9E4')
    style.configure('TButton', background='#c353f5', foreground='white', font=('Arial', 12))
    style.configure('TLabel', background='#FFE9E4', foreground='black', font=('Arial', 12))
    style.configure('TEntry', fieldbackground='#D9EAF7', foreground='#000', font=('Arial', 12))
    style.configure('TCombobox', fieldbackground='#D9EAF7', foreground='#000', font=('Arial', 12))
    style.map('TCombobox', fieldbackground=[('readonly','#D9EAF7')])
    style = ttk.Style()
    style.configure('Small.TButton', font=('Helvetica', 8), padding=2)
    
    frame = ttk.Frame(root, style='TFrame')
    frame.pack(fill='both', expand=True)

    title_label = ttk.Label(frame, text="Wallet Information", font=('Arial', 20), background="#9ca3bd", foreground="black", anchor="center", padding=(0, 10))
    title_label.pack(fill='x')

    panel1 = ttk.Frame(frame, style='TFrame')
    panel1.pack(fill='x', pady=10)

    evm_frame = ttk.Frame(panel1, style='TFrame')
    evm_frame.pack(fill='x', pady=5)
    ttk.Label(evm_frame, text="EVM Address:", font=('Arial', 12,'bold','underline'),foreground='green').pack(side='left', padx=(10, 5))
    evm_label = ttk.Label(evm_frame, text=evm_address, font=('Arial', 12, 'bold'))
    evm_label.pack(side='left')
    evm_copy_button = ttk.Button(evm_frame, text="Copy",style='Small.TButton', command=lambda: copy_to_clipboard(root, evm_address))
    evm_copy_button.pack(side='left', padx=5)

    panel2 = ttk.Frame(frame, style='TFrame')
    panel2.pack(fill='x', pady=10)

    oG_frame = ttk.Frame(panel2, style='TFrame')
    oG_frame.pack(fill='x', pady=5)
    ttk.Label(oG_frame, text="0G Address:", font=('Arial', 12,'bold','underline'),foreground='orange').pack(side='left', padx=(10, 5))
    oG_label = ttk.Label(oG_frame, text=oG_address, font=('Arial', 12, 'bold'))
    oG_label.pack(side='left')
    oG_copy_button = ttk.Button(oG_frame, text="Copy",style='Small.TButton', command=lambda: copy_to_clipboard(root, oG_address))
    oG_copy_button.pack(side='left', padx=5)

    panel3 = ttk.Frame(frame, style='TFrame')
    panel3.pack(fill='both', expand=True, pady=(20, 10))

    tab_control = ttk.Notebook(frame, style='TNotebook')
    tab_transfer = ttk.Frame(tab_control, style='TFrame')
    tab_delegate = ttk.Frame(tab_control, style='TFrame')
    tab_evm_oG_transfer = ttk.Frame(tab_control, style='TFrame')  # New tab for EVM-0g Transfer
    tab_control.add(tab_transfer, text='0G Transfer')
    tab_control.add(tab_delegate, text='Delegate')
    tab_control.add(tab_evm_oG_transfer, text='EVM- Transfer')  # Add the EVM-0g Transfer tab


    
    validators = fetch_validators()
    setup_tab(tab_transfer, "Transfer", validators, oG_address, private_key,root)
    setup_tab(tab_delegate, "Delegate", validators, oG_address, private_key,root)
    setup_tab(tab_evm_oG_transfer, "EVM-0g Transfer", validators, oG_address, private_key, root)  # Setup the new EVM-0g Transfer tab
    
    global balance_label
    balance_label = ttk.Label(frame, text="Please click 'Update Balance' to view balance", style='TLabel')
    balance_label.pack(fill='x', pady=(10, 10))
    update_balance(balance_label, oG_address)

    update_balance_button = ttk.Button(frame, text="Update Balance", command=lambda: update_balance(balance_label, oG_address))
    update_balance_button.pack(fill='x', pady=(10, 10))
    tab_control.pack(expand=1, fill='both', pady=(0, 10))

    logout_button = ttk.Button(frame, text="Logout", command=lambda: mainscreen.show_main_screen(root))
    logout_button.pack(fill='x', pady=(10, 20))

def paste_to_entry(entry_widget, root):
    try:
        # Panodan içeriği al ve Entry widget'ına yapıştır
        content = root.clipboard_get()
        entry_widget.delete(0, tk.END)  # Mevcut içeriği temizle
        entry_widget.insert(0, content)  # Panodaki içeriği yapıştır
    except tk.TclError:
        print("Nothing to paste")



def setup_tab(tab, action_type, validators, oG_address, private_key, root):
    if action_type == "Transfer":
        current_balances = fetch_balances(oG_address)  # Mevcut bakiyeleri çek

        ttk.Label(tab, text='Target Wallet Address:').pack(pady=(10,0))
        
        address_frame = ttk.Frame(tab)  # Adres ve paste butonu için bir frame oluştur
        address_frame.pack(pady=(0,10))

        target_address_entry = ttk.Entry(address_frame, width=60)
        target_address_entry.pack(side=tk.LEFT, padx=(0, 5))  # Entry widget'ı sola yasla

        style = ttk.Style()
        style.configure('Small.TButton', font=('Helvetica', 8), padding=2)
        
        paste_button = ttk.Button(address_frame, text="Paste", style='Small.TButton', command=lambda: paste_to_entry(target_address_entry, root))
        paste_button.pack(side=tk.LEFT)  # Paste butonunu entry'nin yanına yerleştir



        ttk.Label(tab, text='Amount:').pack(pady=(10,0))
        amount_entry_transfer = ttk.Entry(tab, width=20)
        amount_entry_transfer.pack(pady=(0,10))

        max_button = ttk.Button(tab, text="Max", command=lambda: update_max_amount(amount_entry_transfer, oG_address, root))
        max_button.pack(pady=(5, 10))

        ttk.Label(tab, text='Gas (units):').pack(pady=(10,0))
        gas_entry = ttk.Entry(tab, width =20)
        gas_entry.insert(0, "200000")
        gas_entry.pack(pady=(0,10))

        ttk.Label(tab, text='Fee (amount):').pack(pady=(10,0))
        fee_entry = ttk.Entry(tab, width =20)
        fee_entry.insert(0, "15000")
        fee_entry.pack(pady=(0,10))

        # Transfer butonu
        transfer_button = ttk.Button(tab, text='Transfer', command=lambda: perform_transfer(amount_entry_transfer, target_address_entry, fee_entry, gas_entry, oG_address, private_key, root,balance_label))
        transfer_button.pack(pady=(10,20))
        
    elif action_type == "Delegate":
        ttk.Label(tab, text='Validator:').pack(pady=(10,0))
        validator_combobox = ttk.Combobox(tab, values=[v[0] for v in validators], state='readonly', width=40)
        validator_combobox.pack(pady=(0,10))
        validator_combobox.bind('<<ComboboxSelected>>', lambda event: on_validator_selected(event, validators, validator_combobox, oG_address, private_key))

        ttk.Label(tab, text='Amount:').pack(pady=(10,0))
        amount_entry_delegate = ttk.Entry(tab, width=20)
        amount_entry_delegate.pack (pady=(0,10))
        
        max_button = ttk.Button(tab, text="Max", command=lambda: update_max_amount(amount_entry_delegate, oG_address, root))
        max_button.pack(pady=(5, 10))

        ttk.Label(tab, text='Gas (units):').pack(pady=(10,0))
        gas_entry = ttk.Entry(tab, width=20)
        gas_entry.insert(0, "200000")  # Sabit değer olarak gas miktarı
        gas_entry.pack(pady=(0,10))

        ttk.Label(tab, text='Fee (amount):').pack(pady=(10,0))
        fee_entry = ttk.Entry(tab, width=20)
        fee_entry.insert(0, "15000")  # Sabit değer olarak fee miktarı
        fee_entry.pack(pady=(0,10))

        delegate_button = ttk.Button(tab, text='Delegate', command=lambda: perform_delegate(valid_adr, amount_entry_delegate, gas_entry, fee_entry, oG_address, private_key, root,balance_label))
        delegate_button.pack(pady=(10,20))
        
    
    
    
    elif action_type == "EVM-0g Transfer":
        
        ttk.Label(tab, text='Target EVM Wallet Address:').pack(pady=(10,0))
        
        address_frame = ttk.Frame(tab)  # Adres ve paste butonu için bir frame oluştur
        address_frame.pack(pady=(0,10))

        target_address_evm_entry = ttk.Entry(address_frame, width=60)
        target_address_evm_entry.pack(side=tk.LEFT, padx=(0, 5))  # Entry widget'ı sola yasla

        paste_button = ttk.Button(address_frame, text="Paste", style='Small.TButton', command=lambda: paste_to_entry(target_address_evm_entry, root))
        paste_button.pack(side=tk.LEFT)  # Paste butonunu entry'nin yanına yerleştir
        

        ttk.Label(tab, text='Amount (in 0G):').pack(pady=(10,0))  # Adjusted from ETH to 0G since we are transferring 0G
        amount_entry_evm = ttk.Entry(tab, width=20)
        amount_entry_evm.pack(pady=(0,10))

        def on_transfer_click():
            target_address = target_address_evm_entry.get()
            amount_oG = amount_entry_evm.get()
            balances = fetch_balances(oG_address)  # Burada cüzdan adresinizi geçirmelisiniz
            oG_balance = next((item['amount'] for item in balances if item['denom'] == 'ua0gi'), 0)  # 'oG' balance'ı çekiyoruz
            oG_balance = float(oG_balance)  # Balance'ı float'a çeviriyoruz, çünkü string olabilir
            result = perform_evm_transfer(private_key, target_address, amount_oG, oG_balance)
            messagebox.showinfo("Transfer Result", result)
            if "Transaction successful" in result:
                time.sleep(7)
                update_balance(balance_label, oG_address)

            
        transfer_evm_button = ttk.Button(tab, text='Transfer', command=on_transfer_click)
        transfer_evm_button.pack(pady=(20,0))

def perform_evm_transfer(private_key, target_address, amount_oG, oG_balance):
    try:
        amount_oG = float(amount_oG)
        oG_balance = float(oG_balance) / 1e6
        
    except ValueError:
        return "Invalid amount or balance. Please enter a valid number."

    # Kullanılabilir maksimum miktarı bakiye - 0.01 0G olarak hesapla
    max_transferable = oG_balance - 0.01

    if amount_oG > max_transferable:
        return f"Transfer amount exceeds the available balance minus reserve. Maximum transferable: {max_transferable}"

    # Assuming evm_transfer is a function from evmtransfer module that handles the transfer logic
    result = evm_transfer(private_key, target_address, amount_oG)
    return result

    

def on_validator_selected(event, validators, combobox, oG_address, private_key):
    selected_index = combobox.current()
    target_validator_address = validators[selected_index][1]  # İlgili validator adresini al
    print(f"Selected validator address: {target_validator_address}")
    global valid_adr
    valid_adr=target_validator_address
    

