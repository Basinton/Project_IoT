print("Sensors and Actuators")

import time
import serial
import serial.tools.list_ports

# IDs for different types of actuators
fertilizer_mixers = [1, 2, 3]
area_selectors = [4, 5, 6]  # Representing 3 relays for 3 areas
pump_in = 7
pump_out = 8

ser = None  # Global variable to hold the serial port instance

def initialize_modbus(port='COM7', baudrate=115200, timeout=1):
    global ser
    if ser is None:
        try:
            ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
            print(f"Port {port} opened successfully")
        except serial.SerialException as e:
            print(f"Failed to open port {port}: {e}")
            ser = None
    return ser

def getPort():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"Found port: {port.device}")
    return "COM7"  # Use the created virtual port

portName = getPort()
print(f"Using port: {portName}")

initialize_modbus(port=portName)

def serial_read_data():
    bytesToRead = ser.inWaiting()
    if bytesToRead > 0:
        out = ser.read(bytesToRead)
        data_array = [b for b in out]
        print(data_array)
        if len(data_array) >= 7:
            array_size = len(data_array)
            value = data_array[array_size - 4] * 256 + data_array[array_size - 3]
            return value
        else:
            return -1
    return 0

def crc16(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if (crc & 1) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

def add_crc16(data):
    crc = crc16(data)
    crc_high = (crc >> 8) & 0xFF
    crc_low = crc & 0xFF
    return data + [crc_low, crc_high]

def generate_command(device_id, state):
    command = [device_id, 6, 0, 0, 0, 255 if state else 0]
    return add_crc16(command)

def setDevice(device_id, state):
    command = generate_command(device_id, state)
    print(f"Sending command (Device {device_id}, {'ON' if state else 'OFF'}): {command}")
    ser.write(bytearray(command))
    time.sleep(1)
    response = serial_read_data()
    print(f"Response: {response}")

# Example usage for controlling actuators
if ser:
    # Example of controlling fertilizer mixers
    for mixer_id in fertilizer_mixers:
        setDevice(mixer_id, True)  # Turn on
        time.sleep(2)
        setDevice(mixer_id, False)  # Turn off
        time.sleep(2)

# Example of controlling area selectors
    for selector_id in area_selectors:
        setDevice(selector_id, True)  # Activate area
        time.sleep(2)
        setDevice(selector_id, False)  # Deactivate area
        time.sleep(2)

# Example of controlling pumps
    setDevice(pump_in, True)  # Turn on pump in
    time.sleep(2)
    setDevice(pump_in, False)  # Turn off pump in
    time.sleep(2)
    setDevice(pump_out, True)  # Turn on pump out
    time.sleep(2)
    setDevice(pump_out, False)  # Turn off pump out
else:
    print("Serial port is not available. Cannot proceed with setting devices.")
