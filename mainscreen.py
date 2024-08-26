import tkinter as tk
import newwallet
from login_prvtkey import login_screen  # login_prvtkey.py dosyasından fonksiyonu import ediyoruz

def clear_content(root):
    for widget in root.winfo_children():
        widget.destroy()

def show_main_screen(root):
    clear_content(root)
    app_info_label = tk.Label(root, text="0G Desktop Wallet v1.0", font=('Arial', 20), bg='#FFE9E4', fg='black')
    app_info_label.pack()

    logo = tk.PhotoImage(file="logo.png")
    logo_label = tk.Label(root, image=logo, bg='black')
    logo_label.image = logo  # referansı korumak için
    logo_label.pack(pady=(20, 10))

    developer_info_label = tk.Label(root, text="This application is developed by Coinsspor", font=('Arial', 10), bg='#FFE9E4', fg='black')
    developer_info_label.pack()

    frame = tk.Frame(root, bg='#FFE9E4')
    frame.pack(fill='both', expand=True)

    create_wallet_button = tk.Button(frame, text="Create a New Wallet", bg='#c353f5', fg='white', font=('Arial', 14, 'bold'), command=lambda: newwallet.create_new_wallet(root))
    create_wallet_button.pack(fill='x', expand=True, padx=20, pady=(50, 10))

    login_private_key_button = tk.Button(frame, text="Login in With a private key", bg='#c353f5', fg='white', font=('Arial', 14, 'bold'), command=lambda: login_screen(root))
    login_private_key_button.pack(fill='x', expand=True, padx=20, pady=(10, 50))
