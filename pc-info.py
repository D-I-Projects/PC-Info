import psutil
import platform
import cpuinfo
import tkinter as tk
from tkinter import messagebox
import logging
import datetime
import threading
import time
import os
import requests
from tkinter import PhotoImage

def log_settings():
    log_dir = "Log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_filename = os.path.join(log_dir, f"PC-Info - {current_datetime}.log")

    logger = logging.getLogger("PC-Info")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

logger = log_settings()

SYSTEM = platform.system()

def check_internet_connection():
    try:
        response = requests.get("http://www.google.com", timeout=5)
        if response.status_code == 200:
            return True
    except requests.RequestException:
        messagebox.showwarning("Warning", "No internet!")
    return False

def download_icon():
    icon_url = "https://github.com/wfxey/PC-Info/releases/download/v0.1/roundedpi.png"
    file_name = "icon.png"
    try:
        if os.path.exists(file_name):
            logger.info(f"The file {file_name} already exists.")
            return
        
        response = requests.get(icon_url)
        if response.status_code == 200:
            with open(file_name, 'wb') as file:
                file.write(response.content)
            logger.info(f"The icon file has been successfully downloaded and saved as {file_name}.")
        else:
            logger.error(f"Failed to download the icon file. Status code: {response.status_code}")
    except Exception as e:
        logger.error(f"An error occurred while downloading the icon file: {e}")

def gpu_print():
    gpus = prepare_platform()
    if gpus:
        gpu_info = ""
        for gpu in gpus:
            gpu_info += f"GPU Name: {gpu.Name}\n"
            gpu_info += f"GPU Memory Total: {gpu.AdapterRAM // (1024 ** 2)} MB\n"
    else:
        gpu_info = "No GPU information available."
    return gpu_info

download_icon()

root = tk.Tk()
root.title("PC Info")
root.resizable(width=False,height=False)
icon_image = PhotoImage(file="icon.png")
root.wm_iconphoto(True, icon_image)

T = tk.Text(root)
T.pack()
T.config(state="disabled")

def prepare_platform():
    if SYSTEM == "Linux":
        return "/home"
    else:
        root.geometry("800x400")
        import wmi
        w = wmi.WMI()
        return w.Win32_VideoController()

def info_print():
    CPU_INFO = platform.processor()
    CPU_NAME = cpuinfo.get_cpu_info()['brand_raw']
    CPU_COUNT = psutil.cpu_count()
    RAM_AMOUNT = psutil.virtual_memory()
    DISK_USAGE = psutil.disk_usage(os.path.abspath(os.sep))
    EXACT_VERSION = platform.platform()
    ARCHITECTURE = platform.architecture()[0]
    PYTHON_VERSION = platform.python_version()
    
    ram_amount_gb = round(RAM_AMOUNT.total / (1024 ** 3))
    storage_total_gb = round(DISK_USAGE.total / (1024 ** 3))
    storage_used_gb = round(DISK_USAGE.used / (1024 ** 3))
    storage_free_gb = round(DISK_USAGE.free / (1024 ** 3))

    sys_info = (
        f"CPU Info: {CPU_INFO}\n"
        f"CPU Name: {CPU_NAME}\n"
        f"CPU Count: {CPU_COUNT}\n"
        f"RAM Amount: {ram_amount_gb} GB\n"
        f"Storage Total: {storage_total_gb} GB\n"
        f"Storage Used: {storage_used_gb} GB\n"
        f"Storage Free: {storage_free_gb} GB\n"
        f"System: {SYSTEM}\n"
        f"Exact Version: {EXACT_VERSION}\n"
        f"Architecture: {ARCHITECTURE}\n"
        f"Python Version: {PYTHON_VERSION}\n"
    )
    return sys_info

def set_window_text():
    T.config(state="normal")
    T.delete("1.0", tk.END)
    T.insert(tk.END, info_print() + gpu_print()) 
    T.config(state="disabled")

def update_window():
    set_window_text()

def update_information():
    threading.Thread(target=update_window).start()

def on_exit():
    root.destroy()

menubar = tk.Menu(root)
root.config(menu=menubar)
file_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Exit", command=on_exit)

menubar.add_command(label="Update", command=update_information)

update_information()

root.mainloop()
