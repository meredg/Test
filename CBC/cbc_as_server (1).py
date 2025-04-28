import socket
import json
import requests

host = "192.168.3.3"  # CBC machine IP
port = 5100           # CBC machine port

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))  # Connect to CBC machine (acting as server)
print(f"Connected to {host}:{port}")

while True:
    data = client_socket.recv(16 * 1024)  # Receive data
    if not data:
        print("[ERROR] No data received. Closing connection.")
        client_socket.close()
        continue

    lines = data.decode('utf-8').split("\r")

    # Extract CBC parameters
    cbc_results = {}

    # Extract patient name
    for line in lines:
        if line.startswith("PID"):
            parts = line.split("|")
            if len(parts) > 5:
                patient_name = parts[5].replace("^", " ").strip()  # Extract and format name
                cbc_results["Patient Name"] = patient_name
            break  # Stop after finding the name

    # Extract CBC values
    for line in lines:
        if line.startswith("OBX"):
            parts = line.split("|")
            if len(parts) > 5:
                name = parts[3].split("^")[1]  # Extract parameter name
                value = parts[5]  # Extract value
                cbc_results[name] = value

    # Only print if CBC results contain data
    if len(cbc_results) > 1:  # Ensure more than just the patient name exists
        #cbc_json = json.dumps(cbc_results, indent=4)
        #print(cbc_json)
        # Prepare data for sending to Laravel API
        api_url = 'http://192.168.100.99/api/genru-receive-data'
        payload = {
            "data": {
                "patient_name": patient_name,
                **cbc_results  # Merge CBC results into the payload
            }
        }
            
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            
            print(f"[INFO] Response Status: {response.status_code}")
            if response.status_code == 201:
                print("[SUCCESS] Data sent and saved successfully!")
            else:
                print(f"[ERROR] Failed to send data: {response.status_code}, Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] API request failed: {e}")

client_socket.close()
