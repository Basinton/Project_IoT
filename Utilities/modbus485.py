import time
import serial
import serial.tools.list_ports

# IDs for different types of actuators
fertilizer_mixers = [1, 2, 3]
area_selectors = [4, 5, 6]
pump_in = 7
pump_out = 8

def initialize_modbus(port='/dev/ttyUSB0', baudrate=115200, timeout=1):
    try:
        ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        print(f"Port {port} opened successfully")
    except serial.SerialException as e:
        print(f"Failed to open port {port}: {e}")
        ser = None
    return ser

def serial_read_data(ser):
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

def setDevice(ser, device_id, state):
    command = generate_command(device_id, state)
    print(f"Sending command (Device {device_id}, {'ON' if state else 'OFF'}): {command}")
    ser.write(bytearray(command))
    time.sleep(1)
    response = serial_read_data(ser)
    print(f"Response: {response}")

# Example usage for controlling actuators
if __name__ == "__main__":
    ser = initialize_modbus(port='/dev/ttyUSB0')

    if ser:
        # Example of controlling fertilizer mixers
        for mixer_id in fertilizer_mixers:
            setDevice(ser, mixer_id, True)  # Turn on
            time.sleep(2)
            setDevice(ser, mixer_id, False)  # Turn off
            time.sleep(2)

        # Example of controlling area selectors
        for selector_id in area_selectors:
            setDevice(ser, selector_id, True)  # Activate area
            time.sleep(2)
            setDevice(ser, selector_id, False)  # Deactivate area
            time.sleep(2)

        # Example of controlling pumps
        setDevice(ser, pump_in, True)  # Turn on pump in
        time.sleep(2)
        setDevice(ser, pump_in, False)  # Turn off pump in
        time.sleep(2)
        setDevice(ser, pump_out, True)  # Turn on pump out
        time.sleep(2)
        setDevice(ser, pump_out, False)  # Turn off pump out

        ser.close()
    else:
        print("Serial port is not available. Cannot proceed with setting devices.")