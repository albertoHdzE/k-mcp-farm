import requests
import json

BASE_URL = "http://localhost:4444"

def list_gateways():
    try:
        # Try without auth first
        response = requests.get(f"{BASE_URL}/gateways", timeout=5)
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    list_gateways()
