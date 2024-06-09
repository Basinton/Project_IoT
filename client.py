import socket

# Define the server address and port
SERVER_IP = '172.28.182.53'  # Replace with the public IP address of your CM4's network
PORT = 12345

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((SERVER_IP, PORT))

# Send data to the server
client_socket.sendall(b"Hello from client")

# Receive data from the server
data = client_socket.recv(1024)
print(f"Received from server: {data.decode('utf-8')}")

# Close the connection
client_socket.close()
