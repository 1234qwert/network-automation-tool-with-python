import netmiko
import csv
import os
from datetime import datetime

# --- Konfigurasi ---
DEVICES_FILE = 'devices.csv'
COMMANDS_FILE = 'commands.txt'
LOGS_DIR = 'logs'

# --- Fungsi untuk koneksi dan eksekusi perintah ---
def connect_and_execute(device, commands):
    hostname = device['hostname']
    ip_address = device['ip_address']
    username = device['username']
    password = device['password']
    ssh_port = int(device.get('ssh_port', 22))
    
    # Ambil waktu saat ini dan format
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Buat nama file dengan format baru: hostname_data_PM_waktu.log
    log_file_path = os.path.join(LOGS_DIR, f'{hostname}_data_PM_{current_time}.log')
    
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

    try:
        print(f"[*] Menghubungi {hostname} ({ip_address}) di port {ssh_port}...")
        
        net_connect = netmiko.ConnectHandler(
            device_type='cisco_ios',
            host=ip_address,
            port=ssh_port,
            username=username,
            password=password
        )
        
        print(f"[+] Berhasil terhubung ke {hostname}.")
        
        with open(log_file_path, 'w') as f:
            for command in commands:
                print(f"[*] Mengirim perintah: '{command.strip()}' ke {hostname}...")
                
                output = net_connect.send_command(command)
                
                f.write(f"--- Output untuk perintah: {command.strip()} ---\n")
                f.write(output)
                f.write("\n\n")

        net_connect.disconnect()
        print(f"[+] Output berhasil disimpan di {log_file_path}.")

    except netmiko.ssh_exception.NetmikoAuthenticationException:
        print(f"[-] Gagal terhubung ke {hostname}: Authentication failed. Periksa username/password.")
    except Exception as e:
        print(f"[-] Terjadi kesalahan saat menghubungkan ke {hostname}: {e}")

# --- Fungsi utama ---
def main():
    devices = []
    commands = []

    try:
        with open(DEVICES_FILE, 'r') as f:
            reader = csv.DictReader(f, fieldnames=['hostname', 'ip_address', 'username', 'password', 'ssh_port'])
            next(reader) 
            devices = [row for row in reader]
    except FileNotFoundError:
        print(f"[-] File {DEVICES_FILE} tidak ditemukan. Pastikan file ada di lokasi yang benar.")
        return
    
    try:
        with open(COMMANDS_FILE, 'r') as f:
            commands = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[-] File {COMMANDS_FILE} tidak ditemukan. Pastikan file ada di lokasi yang benar.")
        return
    
    if not devices:
        print("[-] Tidak ada perangkat yang ditemukan di devices.csv.")
        return
    
    if not commands:
        print("[-] Tidak ada perintah yang ditemukan di commands.txt.")
        return

    for device in devices:
        connect_and_execute(device, commands)
        print("-" * 50)

if __name__ == "__main__":
    main()