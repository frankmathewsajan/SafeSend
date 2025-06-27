import serial
import time
import json
import csv
import serial.tools.list_ports

# === CONFIGURATION ===
BAUD_RATE = 9600
LOG_FILE = 'health_log.csv'
DURATION = 10  # seconds to log

def get_serial_ports():
    """Returns a set of currently available serial ports."""
    return {port.device for port in serial.tools.list_ports.comports()}

def wait_for_new_serial_port(existing_ports):
    """Waits for a new serial device to be plugged in."""
    print("Waiting for new serial device to be plugged in...")
    while True:
        current_ports = get_serial_ports()
        new_ports = current_ports - existing_ports
        if new_ports:
            return new_ports.pop()
        time.sleep(0.5)

# === STEP 1: Detect current ports
print("Scanning for serial ports...")
before_ports = get_serial_ports()

# === STEP 2: Wait for a new device to be plugged in
selected_port = wait_for_new_serial_port(before_ports)
print(f"New device detected on {selected_port}. Waiting for it to initialize...")
time.sleep(2)  # wait for device to finish initializing

# === STEP 3: Try to connect to serial port
try:
    ser = serial.Serial(selected_port, BAUD_RATE, timeout=1)
    print(f"✅ Connected to {selected_port} at {BAUD_RATE} baud.")
except Exception as e:
    print(f"❌ Failed to connect to {selected_port}: {e}")
    exit()

# === STEP 4: Begin logging to CSV
end_time = time.time() + DURATION
with open(LOG_FILE, 'w', newline='') as csvfile:
    fieldnames = ['timestamp', 'bpm', 'spo2', 'steps', 'fall', 'lat', 'lng']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    print(f"📦 Logging data to '{LOG_FILE}' for {DURATION} seconds...\n")
    while time.time() < end_time:
        if ser.in_waiting:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                data = json.loads(line)
                data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow(data)
                print(data)
            except json.JSONDecodeError:
                print("⚠️ Invalid JSON received:", line)

ser.close()
print(f"\n✅ Logging complete. File saved as '{LOG_FILE}'")
