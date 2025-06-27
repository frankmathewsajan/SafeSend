import serial
import time
import json
import os
import serial.tools.list_ports

# === CONFIGURATION ===
BAUD_RATE = 9600
PORT_FILE = 'last_port.txt'

def get_serial_ports():
    return {port.device for port in serial.tools.list_ports.comports()}

def wait_for_new_serial_port(existing_ports):
    print("Waiting for a new serial device to be plugged in...")
    while True:
        current_ports = get_serial_ports()
        new_ports = current_ports - existing_ports
        if new_ports:
            return new_ports.pop()
        time.sleep(0.5)

def read_last_port():
    if os.path.exists(PORT_FILE):
        with open(PORT_FILE, 'r') as f:
            return f.read().strip()
    return None

def save_last_port(port):
    with open(PORT_FILE, 'w') as f:
        f.write(port)

# === SELECT PORT ===
last_port = read_last_port()
selected_port = None

if last_port:
    print("Previously used port detected:")
    print(f"1. Use previous port: {last_port}")
    print("2. Detect new device")
    choice = input("Select option (1 or 2): ").strip()
    if choice == '1':
        selected_port = last_port
    elif choice == '2':
        before_ports = get_serial_ports()
        selected_port = wait_for_new_serial_port(before_ports)
    else:
        print("Invalid choice. Exiting.")
        exit()
else:
    print("No previously used port found. Detecting new device...")
    before_ports = get_serial_ports()
    selected_port = wait_for_new_serial_port(before_ports)

print(f"Selected port: {selected_port}")
print("Waiting 2 seconds for device to initialize...")
time.sleep(2)

# === CONNECT TO SERIAL ===
try:
    ser = serial.Serial(selected_port, BAUD_RATE, timeout=1)
    print(f"✅ Connected to {selected_port} at {BAUD_RATE} baud.")
    save_last_port(selected_port)
except Exception as e:
    print(f"❌ Failed to connect to {selected_port}: {e}")
    exit()

# === INFINITE LIVE OUTPUT ===
print(f"\n📟 Reading serial data. Press Ctrl+C to stop.\n")
try:
    while True:
        if ser.in_waiting:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                data = json.loads(line)
                print(data)
            except json.JSONDecodeError:
                print("⚠️ Invalid JSON received:", line)
except KeyboardInterrupt:
    print(f"\n🛑 Keyboard interrupt detected. Stopping...")
finally:
    ser.close()
    print(f"✅ Serial port {selected_port} closed.")
