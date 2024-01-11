import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
import time
import hashlib
from pathlib import Path
import pyperclip
import subprocess

def load_codes_and_values():
    file_path = Path.home() / "motp_settings.txt"
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        return []

def save_account(name, code, timezone, use_putty, host="", port="", username=""):
    file_path = Path.home() / "motp_settings.txt"
    with open(file_path, 'a') as file:
        if use_putty:
            file.write(f"{name} - {code} - {timezone} - {host} - {port} - {username}\n")
        else:
            file.write(f"{name} - {code} - {timezone}\n")

def add_account(selected_option, connect_button):
    name = simpledialog.askstring("Add Account", "Enter the account name:")
    if not name:
        messagebox.showerror("Error", "All fields must be filled.")
        return

    code = simpledialog.askstring("Add Account", "Enter the account code:")
    if not code:
        messagebox.showerror("Error", "All fields must be filled.")
        return

    timezone = simpledialog.askstring("Add Account", "Enter the account timezone:")
    if not timezone:
        messagebox.showerror("Error", "All fields must be filled.")
        return

    use_putty = messagebox.askyesno("Use PuTTY", "Do you want to add PuTTY configuration?")

    host, port, username = "", "", ""
    if use_putty:
        host = simpledialog.askstring("PuTTY Configuration", "Enter the host:")
        port = simpledialog.askstring("PuTTY Configuration", "Enter the port:")
        username = simpledialog.askstring("PuTTY Configuration", "Enter the username:")

    save_account(name, code, timezone, use_putty, host, port, username)
    messagebox.showinfo("Success", "The account has been added.")

    # Reload the list of accounts
    load_and_reload_options(selected_option, connect_button)

def generate_pin(selected_index, result_label, connect_button):
    codes_and_values = load_codes_and_values()
    if not codes_and_values:
        messagebox.showerror("Error", "No data in the motp_settings.txt file.")
        return

    name, code, timezone, *putty_config = codes_and_values[selected_index].split(" - ")
    epoch = int(time.time())
    pin = pin_entry.get()

    generated_code = hashlib.md5(b"%d%s%s" % (epoch // 10, code.encode('ascii'), pin.encode('ascii'))).hexdigest()[:6]

    for widget in result_label.winfo_children():
        widget.destroy()

    result_widget = tk.Label(result_label, text=f"Generated PIN for {name}: ", font=("Arial", 11))
    result_widget.pack(side=tk.LEFT)

    result_widget_bold = tk.Label(result_label, text=f"{generated_code}", font=("Arial", 16, "bold"))
    result_widget_bold.pack(side=tk.LEFT)

    pyperclip.copy(generated_code)
    pin_entry.delete(0, tk.END)

    if putty_config and putty_config[0]:  # Check if host is set in the configuration
        connect_button["state"] = tk.NORMAL  # Enable the Connect button
        connect_button["command"] = lambda: connect_putty(putty_config[0], putty_config[1], putty_config[2])
    else:
        connect_button["state"] = tk.DISABLED  # Disable the Connect button

def on_generate_click(result_label, connect_button):
    if selected_option:
        generate_pin(selected_option.current(), result_label, connect_button)

def edit_data(selected_option, connect_button):
    file_path = Path.home() / "motp_settings.txt"
    try:
        subprocess.run(["notepad.exe", file_path], check=True)
        # After editing the file, reload the list of accounts
        load_and_reload_options(selected_option, connect_button)
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "No data in the motp_settings.txt file.")

def load_and_reload_options(selected_option, connect_button):
    options = load_codes_and_values()
    if options:
        names = [option.split(" - ")[0] for option in options]
        selected_option["values"] = names
        selected_option.set(names[0])
    else:
        if selected_option:  # Check if selected_option exists
            selected_option["values"] = []

    connect_button["state"] = tk.DISABLED  # Disable the Connect button initially

def connect_putty(host, port, username):
    command = "putty.exe "
    if username:
        command += f"{username}@{host}"
    else:
        command += host

    if port:
        command += f" -P {port}"

    subprocess.run(command, shell=True)

# Main window
root = tk.Tk()
root.title("MOTP")

menu = tk.Menu(root)
root.config(menu=menu)

submenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Options", menu=submenu)
submenu.add_command(label="Add Account", command=lambda: add_account(selected_option, connect_button))
submenu.add_command(label="Edit Data", command=lambda: edit_data(selected_option, connect_button))
submenu.add_command(label="Exit", command=root.destroy)

label = tk.Label(root, text="Enter 4 digits:")
label.grid(row=0, column=0, pady=10, padx=10, sticky="w")

pin_entry = tk.Entry(root, width=10, show="*")
pin_entry.grid(row=1, column=0, pady=10, padx=10, sticky="w")

# Initialize selected_option variable before using it
selected_option = None

options = load_codes_and_values()
if not options:
    # If the file doesn't exist, call the add_account function on OK button click
    user_response = messagebox.showinfo("Welcome", "This appears to be your first run. Please add an account.")
    if user_response == 'ok':
        selected_option = ttk.Combobox(root, values=[], state="readonly")
        selected_option.set('')
        selected_option.grid(row=2, column=0, pady=10, padx=10, sticky="w")

        generate_button = tk.Button(root, text="Generate", command=lambda: on_generate_click(result_label, connect_button))
        generate_button.grid(row=3, column=0, pady=10, padx=10, sticky="w")

        connect_button = tk.Button(root, text="Connect", state=tk.DISABLED)
        connect_button.grid(row=3, column=1, pady=10, padx=10, sticky="w")

        result_label = tk.Label(root, text="", font=("Arial", 12))
        result_label.grid(row=4, column=0, pady=10, padx=10, sticky="w")
else:
    names = [option.split(" - ")[0] for option in options]
    selected_option = ttk.Combobox(root, values=names, state="readonly")
    selected_option.set(names[0])
    selected_option.grid(row=2, column=0, pady=10, padx=10, sticky="w")

    generate_button = tk.Button(root, text="Generate", command=lambda: on_generate_click(result_label, connect_button))
    generate_button.grid(row=3, column=0, pady=10, padx=10, sticky="w")

    connect_button = tk.Button(root, text="Connect", state=tk.DISABLED, command=lambda: connect_putty("", "", ""))
    connect_button.grid(row=3, column=1, pady=10, padx=10, sticky="w")

    result_label = tk.Label(root, text="", font=("Arial", 12))
    result_label.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="w")

root.mainloop()
