import hashlib
import os
import platform
import random
import re
import struct
import subprocess
import tempfile
import uuid
from tkinter import filedialog

import requests
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

SERVER_URL = "http://127.0.0.1:5000/activate"
BLOCK_SIZE = 1024


# -----------------------------
# HASH FILE
# -----------------------------
def hash_file(path):
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()


# -----------------------------
# HARDWARE PROFILE
# -----------------------------
def collect_hardware_profile():
    return {
        "cpu": platform.processor(),
        "machine": platform.machine(),
        "system": platform.system(),
        "node": platform.node(),
        "mac": hex(uuid.getnode()),
    }


# -----------------------------
# SCRAMBLE RESTORE SYSTEM
# -----------------------------
def get_seed_from_key(key: str) -> int:
    return int(hashlib.sha256(key.encode()).hexdigest(), 16)


def generate_permutation(length: int, key: str):
    rng = random.Random(get_seed_from_key(key))
    indices = list(range(length))
    rng.shuffle(indices)
    return indices


def split_blocks(data: bytes):
    return [data[i : i + BLOCK_SIZE] for i in range(0, len(data), BLOCK_SIZE)]


def restore_and_execute(scrambled_exe, key):

    with open(scrambled_exe, "rb") as f:
        original_size = struct.unpack(">Q", f.read(8))[0]
        data = f.read()

    blocks = split_blocks(data)

    permutation = generate_permutation(len(blocks), key)

    restored_blocks = [None] * len(blocks)

    for i, perm_index in enumerate(permutation):
        restored_blocks[perm_index] = blocks[i]

    restored_data = b"".join(restored_blocks)
    restored_data = restored_data[:original_size]

    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, "syscache_tmp.exe")

    with open(temp_path, "wb") as f:
        f.write(restored_data)

    os.chmod(temp_path, 0o775)

    subprocess.Popen([temp_path])

    print("[+] Protected program launched")


# -----------------------------
# LAUNCHER UI
# -----------------------------
class Launcher:
    def __init__(self):

        self.main_path = None

        self.app = ttk.Window(themename="darkly")
        self.app.title("Product Activation")
        self.app.geometry("520x320")
        self.app.resizable(False, False)

        container = ttk.Frame(self.app, padding=20)
        container.pack(fill=BOTH, expand=True)

        ttk.Label(
            container,
            text="Product Activation",
            font=("Segoe UI", 18, "bold"),
        ).pack(pady=10)

        ttk.Label(container, text="License Key").pack(anchor=W)

        self.license_entry = ttk.Entry(container, font=("Segoe UI", 11))
        self.license_entry.pack(fill=X, pady=5)

        file_frame = ttk.Frame(container)
        file_frame.pack(fill=X, pady=10)

        ttk.Button(
            file_frame,
            text="Browse scrambled.exe",
            bootstyle="secondary",
            command=self.browse,
        ).pack(side=LEFT)

        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.pack(side=LEFT, padx=10)

        ttk.Button(
            container,
            text="Activate & Run",
            bootstyle="success",
            command=self.activate,
        ).pack(fill=X, pady=15)

        self.status = ttk.Label(container, text="Ready")
        self.status.pack()

    def browse(self):

        path = filedialog.askopenfilename(
            title="Select scrambled executable",
            filetypes=[("All files", "*.*")],
        )

        if path:
            self.main_path = path
            self.file_label.config(text=path)

    def valid_license(self, key):

        pattern = r"^[A-Za-z0-9]{4}(-[A-Za-z0-9]{4}){3}$"
        return re.match(pattern, key)

    def activate(self):

        license_key = self.license_entry.get().strip()

        if not self.valid_license(license_key):
            ttk.dialogs.Messagebox.show_error("License must be XXXX-XXXX-XXXX-XXXX")
            return

        if not self.main_path:
            ttk.dialogs.Messagebox.show_error("Please select the executable")
            return

        try:
            self.status.config(text="Hashing executable...")
            exe_hash = hash_file(self.main_path)

            self.status.config(text="Collecting hardware profile...")
            hardware_profile = collect_hardware_profile()

            payload = {
                "license_key": license_key,
                "exe_hash": exe_hash,
                "hardware_profile": hardware_profile,
            }
            print(payload)

            self.status.config(text="Contacting activation server...")

            response = requests.post(SERVER_URL, json=payload, timeout=10)

            data = response.json()

            if data.get("status") == "activated":
                activation_key = data.get("activation_key")

                self.status.config(text="Activation successful")

                restore_and_execute(self.main_path, activation_key)

            else:
                ttk.dialogs.Messagebox.show_error(
                    data.get("message", "Activation failed")
                )

        except Exception as e:
            ttk.dialogs.Messagebox.show_error(str(e))

    def run(self):
        self.app.mainloop()


if __name__ == "__main__":
    Launcher().run()
