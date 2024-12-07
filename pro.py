import tkinter as tk
from tkinter import messagebox
import sqlite3
from cryptography.fernet import Fernet
import base64
import os

# Generate a key for encryption
def generate_key():
    return Fernet.generate_key()

# Encrypt the password
def encrypt_password(password, key):
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(password.encode())
    return encrypted_password

# Decrypt the password
def decrypt_password(encrypted_password, key):
    fernet = Fernet(key)
    decrypted_password = fernet.decrypt(encrypted_password).decode()
    return decrypted_password

# Create the database and table
def create_database():
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY,
            website TEXT NOT NULL,
            username TEXT NOT NULL,
            password BLOB NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Add a new password
def add_password(website, username, password, key):
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    encrypted_password = encrypt_password(password, key)
    cursor.execute('INSERT INTO passwords (website, username, password) VALUES (?, ?, ?)',
                   (website, username, encrypted_password))
    conn.commit()
    conn.close()

# Retrieve a password
def get_password(website, key):
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, password FROM passwords WHERE website=?', (website,))
    result = cursor.fetchone()
    conn.close()
    if result:
        username, encrypted_password = result
        decrypted_password = decrypt_password(encrypted_password, key)
        return username, decrypted_password
    else:
        return None, None

# GUI Setup
class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")

        self.key = generate_key()
        create_database()

        self.website_label = tk.Label(root, text="Website:")
        self.website_label.pack()
        self.website_entry = tk.Entry(root)
        self.website_entry.pack()

        self.username_label = tk.Label(root, text="Username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        self.password_label = tk.Label(root, text="Password:")
        self.password_label.pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        self.add_button = tk.Button(root, text="Add Password", command=self.add_password)
        self.add_button.pack()

        self.retrieve_button = tk.Button(root, text="Retrieve Password", command=self.retrieve_password)
        self.retrieve_button.pack()

        self.result_label = tk.Label(root, text="")
        self.result_label.pack()

    def add_password(self):
        website = self.website_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        if website and username and password:
            add_password(website, username, password, self.key)
            messagebox.showinfo("Success", "Password added successfully!")
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields.")

    def retrieve_password(self):
        website = self.website_entry.get()
        if website:
            username, decrypted_password = get_password(website, self.key)
            if username and decrypted_password:
                self.result_label.config(text=f"Username: {username}\nPassword: {decrypted_password}")
            else:
                messagebox.showinfo("Not Found", "No password found for this website.")
        else:
            messagebox.showwarning("Input Error", "Please enter a website.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()

