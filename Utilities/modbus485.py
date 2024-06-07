import time
import serial
import serial.tools.list_ports

soil_temperature = [10, 3, 0, 6, 0, 1, 100, 11]
soil_moisture = [10, 3, 0, 7, 0, 1, 53, 203]

ser = None  # Global variable to hold the serial port instance

def initialize_modbus(port='/dev/ttyUSB0', baudrate=9600):
    global ser
    if ser is None:
        try:
            ser = serial.Serial(port=port, baudrate=baudrate)
            print(f"Port {port} opened successfully")
        except serial.SerialException as e:
            print(f"Failed to open port {port}: {e}")
            ser = None
    return ser

def serial_read_data(ser):
    bytes_to_read = ser.inWaiting()
    if bytes_to_read > 0:
        out = ser.read(bytes_to_read)
        data_array = [b for b in out]
        print(f"Received data: {data_array}")
        if len(data_array) >= 7:
            array_size = len(data_array)
            value = data_array[array_size - 4] * 256 + data_array[array_size - 3]
            return value
        else:
            return -1
    return 0

def readTemperature():
    serial_read_data(ser)
    ser.write(soil_temperature)
    time.sleep(1)
    return serial_read_data(ser)

def readMoisture():
    serial_read_data(ser)
    ser.write(soil_moisture)
    time.sleep(1)
    return serial_read_data(ser)

if __name__ == "__main__":
    ser = initialize_modbus(port='/dev/ttyUSB0')

    if ser:
        while True:
            print("TEST SENSOR")
            print("Moisture:", readMoisture())
            time.sleep(1)
            print("Temperature:", readTemperature())
            time.sleep(1)
    else:
        print("Serial port is not available. Cannot proceed with reading sensors.")
