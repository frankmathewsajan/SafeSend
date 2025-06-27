import serial
import time
import json
import csv
import serial.tools.list_ports

# === CONFIGURATION ===
BAUD_RATE = 9600
LOG_FILE = 'health_log.csv'
DURATION = 10  # seconds

def get_serial_ports():
    return {port.device for port in serial.tools.list_ports.comports()}

def wait_for_new_serial_port(existing_ports):
    print("Waiting for new serial device to be plugged in...")
    while True:
        current_ports = get_serial_ports()
        new_ports = current_ports - existing_ports
        if new_ports:
            return new_ports.pop()
        time.sleep(0.5)

# === STEP 1: Detect initial ports
print("Scanning for serial ports...")
before_ports = get_serial_ports()

# === STEP 2: Wait for new device
selected_port = wait_for_new_serial_port(before_ports)
print(f"New device detected on {selected_port}")

# === STEP 3: Connect and start logging
try:
    ser = serial.Serial(selected_port, BAUD_RATE, timeout=1)
    print(f"Connected to {selected_port} at {BAUD_RATE} baud.")
except Exception as e:
    print(f"Failed to connect: {e}")
    exit()

# === STEP 4: Start CSV logging ===
end_time = time.time() + DURATION
with open(LOG_FILE, 'w', newline='') as csvfile:
    fieldnames = ['timestamp', 'bpm', 'spo2', 'steps', 'fall', 'lat', 'lng']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    print(f"Logging JSON data to {LOG_FILE} for {DURATION} seconds...")
    while time.time() < end_time:
        if ser.in_waiting:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                data = json.loads(line)
                data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow(data)
                print(data)
            except json.JSONDecodeError:
                print("Invalid JSON:", line)

ser.close()
print(f"✅ Logging complete. File saved as {LOG_FILE}")
