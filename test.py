import socket
import requests

# Function to get the public IP address
def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=text')
        public_ip = response.text
    except requests.RequestException as e:
        public_ip = "Unable to get public IP"
        print(f"Error: {e}")
    return public_ip

# Get the public IP address
public_ip = get_public_ip()
print(f"Public IP Address: {public_ip}")

# Define the server address and port
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 12345      # Port to listen on

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address and port
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen()

print(f"Server listening on {HOST}:{PORT}")

while True:
    # Accept a new connection
    client_socket, client_address = server_socket.accept()
    print(f"Connected by {client_address}")

    # Receive data from the client
    data = client_socket.recv(1024)
    if not data:
        break

    print(f"Received from client: {data.decode('utf-8')}")

    # Send a response back to the client
    client_socket.sendall(b"Hello from server")

    # Close the client connection
    client_socket.close()
