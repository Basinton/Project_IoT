import socket

def connect_to_server(server_ip, port=12345):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, port))
        print(f"Connected to server at {server_ip}:{port}")
        s.sendall(b'Hello, Server!')
        data = s.recv(1024)
        print(f"Received data: {data.decode()}")

if __name__ == "__main__":
    server_ip = '125.235.238.108'  # Replace with the IP address of your computer
    connect_to_server(server_ip)
