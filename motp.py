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

def save_account(name, code, timezone):
    file_path = Path.home() / "motp_settings.txt"
    with open(file_path, 'a') as file:
        file.write(f"{name} - {code} - {timezone}\n")

def add_account(selected_option):
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

    save_account(name, code, timezone)
    messagebox.showinfo("Success", "The account has been added.")

    #Reload the list of accounts
    load_and_reload_options(selected_option)

def generate_pin(selected_index, result_label):
    codes_and_values = load_codes_and_values()
    if not codes_and_values:
        messagebox.showerror("Error", "No data in the motp_settings.txt file.")
        return

    name, code, timezone = codes_and_values[selected_index].split(" - ")
    epoch = int(time.time())
    pin = pin_entry.get()

    generated_code = hashlib.md5(b"%d%s%s" % (epoch // 10, code.encode('ascii'), pin.encode('ascii'))).hexdigest()[:6]

    for widget in result_label.winfo_children():
        widget.destroy()

    result_widget = tk.Label(result_label, text=f"Generated PIN for {name}: ", font=("Arial", 12))
    result_widget.pack(side=tk.LEFT)

    result_widget_bold = tk.Label(result_label, text=f"{generated_code}", font=("Arial", 16, "bold"))
    result_widget_bold.pack(side=tk.LEFT)

    pyperclip.copy(generated_code)
    pin_entry.delete(0, tk.END)

def on_generate_click(result_label):
    if selected_option:
        generate_pin(selected_option.current(), result_label)

def edit_data(selected_option):
    file_path = Path.home() / "motp_settings.txt"
    try:
        subprocess.run(["notepad.exe", file_path], check=True)
        # After editing the file, reload the list of accounts
        load_and_reload_options(selected_option)
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "No data in the motp_settings.txt file.")

def load_and_reload_options(selected_option):
    options = load_codes_and_values()
    if options:
        names = [option.split(" - ")[0] for option in options]
        selected_option["values"] = names
        selected_option.set(names[0])
    else:
        if selected_option:  # Check if selected_option exists
            selected_option["values"] = []
        messagebox.showerror("Error", "No data in the motp_settings.txt file.")

# Main window
root = tk.Tk()
root.title("MOTP")

menu = tk.Menu(root)
root.config(menu=menu)

submenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Options", menu=submenu)
submenu.add_command(label="Add Account", command=lambda: add_account(selected_option))
submenu.add_command(label="Edit Data", command=lambda: edit_data(selected_option))
submenu.add_command(label="Exit", command=root.destroy)

label = tk.Label(root, text="Enter 4 digits:")
label.pack()

pin_entry = tk.Entry(root, width=10, show="*")
pin_entry.pack()

# Initialize selected_option variable before using it
selected_option = None

options = load_codes_and_values()
if not options:
    # If the file doesn't exist, call the add_account function on OK button click
    user_response = messagebox.showinfo("Welcome", "This appears to be your first run. Please add an account.")
    if user_response == 'ok':
        selected_option = ttk.Combobox(root, values=[], state="readonly")
        selected_option.set('')
        selected_option.pack(pady=10)
        generate_button = tk.Button(root, text="Generate", command=lambda: on_generate_click(result_label))
        generate_button.pack(pady=10)

        result_label = tk.Label(root, text="", font=("Arial", 12))
        result_label.pack()

        # Add an account on OK button click
        add_account(selected_option)
else:
    names = [option.split(" - ")[0] for option in options]
    selected_option = ttk.Combobox(root, values=names, state="readonly")
    selected_option.set(names[0])
    selected_option.pack(pady=10)

    generate_button = tk.Button(root, text="Generate", command=lambda: on_generate_click(result_label))
    generate_button.pack(pady=10)

    result_label = tk.Label(root, text="", font=("Arial", 12))
    result_label.pack()

root.mainloop()
