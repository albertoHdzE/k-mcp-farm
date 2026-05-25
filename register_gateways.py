import requests
import json

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluQGV4YW1wbGUuY29tIiwiaWF0IjoxNzc5NzExNzc4LCJpc3MiOiJtY3BnYXRld2F5IiwiYXVkIjoibWNwZ2F0ZXdheS1hcGkiLCJqdGkiOiIyMDcyYjU2MS01YTgzLTRjZWMtYTlhZC1hMjhiNWY4YWUwZGQiLCJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsImV4cCI6MTc4MDMxNjU3OH0.BuEzHQSX6Ac_wwSqUmg222B1h5yZh7mojy_vi8V_4XM"
BASE_URL = "http://127.0.0.1:4444"

gateways = [
    {
        "name": "GitLab",
        "url": "https://gitlab.com/api/v4/mcp",
        "transport": "STREAMABLEHTTP",
        "auth_type": "oauth",
        "oauth_config": {
            "issuer": "https://gitlab.com",
            "grant_type": "authorization_code",
            # We assume DCR will handle the rest if enabled
        },
        "description": "GitLab Federated MCP Server"
    }
]

def register():
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    for gw in gateways:
        print(f"Registering {gw['name']}...")
        response = requests.post(f"{BASE_URL}/gateways", json=gw, headers=headers)
        if response.status_code in (200, 201):
            print(f"Successfully registered {gw['name']}")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Failed to register {gw['name']}: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    register()
