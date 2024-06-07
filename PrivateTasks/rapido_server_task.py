import requests

class RapidoServerTask:
    def __init__(self):
        pass

    def uploadData(self):
        # Implementation of uploadData
        data = {"key": "value"}  # Replace with actual data
        response = requests.post("http://example.com/upload", json=data)
        print(f"Uploading data to server: {response.status_code}")