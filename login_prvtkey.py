import tkinter as tk
from tkinter import PhotoImage, messagebox
import mainscreen
from eth_keys import keys
from eth_utils import keccak
import bech32
import walletaction

def clear_content(root):
    for widget in root.winfo_children():
        widget.destroy()

def paste_text(entry_widget, root):
    try:
        # Clipboard'tan metni al ve Entry widget'ına yapıştır
        text = root.clipboard_get()
        entry_widget.insert(tk.END, text)
    except tk.TclError:
        pass  # Clipboard boşsa, hata mesajı gösterme

def create_context_menu(root, entry_widget):
    # Sağ tık menüsü oluştur
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Paste", command=lambda: paste_text(entry_widget, root))
    # Menüyü yapılandır
    def show_menu(event):
        menu.post(event.x_root, event.y_root)
    entry_widget.bind("<Button-3>", show_menu)  # Sağ tık ile menüyü göster

def login_screen(root):
    clear_content(root)

    # Logo ve metin ekleyin
    logo_image = PhotoImage(file="logo.png")
    logo_label = tk.Label(root, image=logo_image)
    logo_label.image = logo_image  # referansı korumak için
    logo_label.pack(pady=(20, 0))

    title_label = tk.Label(root, text="Please enter your private key", font=("Arial", 14))
    title_label.pack(pady=(10, 20))

    # Özel anahtar için metin kutusu
    prvt_key_entry = tk.Entry(root, font=("Arial", 14), width=50)
    prvt_key_entry.pack(pady=(0, 20))
    prvt_key_entry.bind("<Control-v>", lambda event: paste_text(prvt_key_entry, root))  # Ctrl+V ile yapıştırma işlevini ekle
    create_context_menu(root, prvt_key_entry)  # Sağ tık menüsünü ekleyin

    # Yapıştırma butonu
    paste_button = tk.Button(root, text="Paste", font=("Arial", 10), bg='lightblue', command=lambda: paste_text(prvt_key_entry, root))
    paste_button.pack(pady=(5, 20))

    # Butonlar
    next_button = tk.Button(root, text="Next", font=("Arial", 12), bg='#c353f5', fg='white', command=lambda: process_private_key(prvt_key_entry.get(), root))
    next_button.pack(fill='x', expand=True, pady=(10, 2))

    back_button = tk.Button(root, text="Back", font=("Arial", 12), bg='#c353f5', fg='white', command=lambda: mainscreen.show_main_screen(root))
    back_button.pack(fill='x', expand=True, pady=(2, 10))

def process_private_key(private_key_hex, root):
    try:
        # "0x" ifadesini kaldırma
        if private_key_hex.startswith("0x"):
            private_key_hex = private_key_hex[2:]

        # Ethereum ve MX adreslerini hesaplama
        eth_address, oG_address = get_wallet_addresses_from_private_key(private_key_hex)
        if eth_address and oG_address:
            # walletaction.py'daki wallet_actions fonksiyonunu çağırarak adres bilgilerini göster
            walletaction.wallet_actions(root, eth_address, oG_address, private_key_hex)
        else:
            messagebox.showerror("Error", "Invalid private key. Please check and try again.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def get_wallet_addresses_from_private_key(private_key_hex):
    # Hex formatındaki özel anahtarı bytes'a çevirme
    priv_key_bytes = bytes.fromhex(private_key_hex)
    
    # Özel anahtarın geçerli olup olmadığını kontrol etme
    if len(priv_key_bytes) != 32:
        messagebox.showerror("Error", "Invalid private key length.")
        return None, None
    
    # Ethereum anahtarlarını hesaplama
    priv_key = keys.PrivateKey(priv_key_bytes)
    pub_key = priv_key.public_key
    eth_address = pub_key.to_checksum_address()

    # Ethereum adresini MX adresine dönüştürme
    oG_address = eth_to_oG_address(eth_address)

    return eth_address, oG_address

def eth_to_oG_address(eth_address):
    addr_hex = eth_address.lower().replace('0x', '')
    addr_bytes = bytes.fromhex(addr_hex)
    data = bech32.convertbits(addr_bytes, 8, 5)
    if data is None:
        messagebox.showerror("Error", "Error in converting bits.")
        return None
    oG_address = bech32.bech32_encode('0g', data)
    return oG_address
