import requests
import json
import time

# --- Configuration ---
BASE_URL = "http://localhost:4444"
# Use the token we just generated
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluQGV4YW1wbGUuY29tIiwiaWF0IjoxNzc5MzY1OTg0LCJpc3MiOiJtY3BnYXRld2F5IiwiYXVkIjoibWNwZ2F0ZXdheS1hcGkiLCJqdGkiOiI1NjFkMWVmMS02OTRkLTQ0YzAtYWJlMi0wNDhmMDAxM2UwNjIiLCJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsInVzZXIiOnsiZW1haWwiOiJhZG1pbkBleGFtcGxlLmNvbSIsImZ1bGxfbmFtZSI6IkNMSSBVc2VyIiwiaXNfYWRtaW4iOnRydWUsImF1dGhfcHJvdmlkZXIiOiJjbGkifSwidGVhbXMiOm51bGwsImV4cCI6MTc3OTk3MDc4NH0.ewScbGjgKroYlFHo9k1YMxqVjeaZ6zE5t9dwn_y-XyE"

def get_list(response_json, key):
    if isinstance(response_json, list):
        return response_json
    if isinstance(response_json, dict):
        return response_json.get(key, [])
    return []

def test_scenarios():
    print("=== ContextForge Scenario Verification ===")
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # 1. Get the list of tools to confirm registration
    print("\n[1] Verifying Tool Registration...")
    try:
        response = requests.get(f"{BASE_URL}/tools", headers=headers)
        if response.status_code != 200:
            print(f"    Failed to list tools: {response.status_code} - {response.text}")
            return

        tools_response = response.json()
        tools = get_list(tools_response, "tools")
        
        print(f"    Total tools found: {len(tools)}")
        # Accept both underscore and hyphenated versions
        target_names = [
            "external_api_post_lookup", "external-api-post-lookup",
            "utility_echo", "utility-echo"
        ]
        scenario_tools = [t for t in tools if t.get('name') in target_names]
        
        for t in scenario_tools:
            print(f"    - {t.get('name')} (Reachable: {t.get('reachable')})")

        if not scenario_tools:
            print("    Warning: No scenario tools found. Check names if they appear in debug list below:")
            for t in tools[:5]:
                print(f"      - {t.get('name')}")
    except Exception as e:
        print(f"    Discovery Error: {e}")
        scenario_tools = []

    # 2. Test External API Scenario
    print("\n[2] Testing External API Scenario (JSONPlaceholder)...")
    ext_api_name = next((t.get('name') for t in scenario_tools if "external" in t.get('name', '')), "external-api-post-lookup")
    
    rpc_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": ext_api_name,
            "arguments": {"id": "1"}
        },
        "id": "1"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/mcp", json=rpc_payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                print(f"    Success: Received response from external API.")
                content = result["result"].get("content", [])
                if content:
                    print(f"    Data: {content[0].get('text')[:100]}...")
            else:
                print(f"    RPC Error: {result.get('error')}")
        else:
            print(f"    HTTP Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"    Request Error: {e}")

    # 3. Test Utility Function Scenario
    print("\n[3] Testing Utility Function Scenario (Echo)...")
    util_echo_name = next((t.get('name') for t in scenario_tools if "utility" in t.get('name', '')), "utility-echo")
    rpc_payload["params"] = {
        "name": util_echo_name,
        "arguments": {"message": "Hello from ContextForge Utility Test!"}
    }
    rpc_payload["id"] = "2"
    
    try:
        response = requests.post(f"{BASE_URL}/mcp", json=rpc_payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                print(f"    Success: Utility echo returned.")
                content = result["result"].get("content", [])
                if content:
                    print(f"    Echo: {content[0].get('text')[:100]}...")
            else:
                print(f"    RPC Error: {result.get('error')}")
        else:
            print(f"    HTTP Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"    Request Error: {e}")

    # 4. Test Knowledge Context Scenario
    print("\n[4] Testing Knowledge Context (Resource)...")
    try:
        response = requests.get(f"{BASE_URL}/resources", headers=headers)
        if response.status_code == 200:
            resources = get_list(response.json(), "resources")
            kb_resource = next((r for r in resources if "knowledge_base.md" in r.get('uri', '')), None)
            if kb_resource:
                print(f"    Found Resource: {kb_resource.get('name')} ({kb_resource.get('uri')})")
                rpc_payload = {
                    "jsonrpc": "2.0",
                    "method": "resources/read",
                    "params": {"uri": kb_resource.get('uri')},
                    "id": "3"
                }
                response = requests.post(f"{BASE_URL}/mcp", json=rpc_payload, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    if "result" in result:
                        print("    Success: Resource content retrieved.")
                        contents = result["result"].get("contents", [])
                        if contents:
                            print(f"    Content Preview: {contents[0].get('text')[:100]}...")
                    else:
                        print(f"    RPC Error: {result.get('error')}")
            else:
                print("    Warning: Knowledge Base resource not found in registry.")
    except Exception as e:
        print(f"    Resource Error: {e}")

    # 5. Test Prompt Template Scenario
    print("\n[5] Testing Prompt Template...")
    try:
        response = requests.get(f"{BASE_URL}/prompts", headers=headers)
        if response.status_code == 200:
            prompts = get_list(response.json(), "prompts")
            welcome_prompt = next((p for p in prompts if p.get('name') in ["welcome_prompt", "welcome-prompt"]), None)
            if welcome_prompt:
                print(f"    Found Prompt: {welcome_prompt.get('name')}")
                rpc_payload = {
                    "jsonrpc": "2.0",
                    "method": "prompts/get",
                    "params": {
                        "name": welcome_prompt.get('name'),
                        "arguments": {"name": "Agent Smith", "task": "security audit"}
                    },
                    "id": "4"
                }
                response = requests.post(f"{BASE_URL}/mcp", json=rpc_payload, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    if "result" in result:
                        print("    Success: Prompt rendered.")
                        messages = result["result"].get("messages", [])
                        if messages:
                            print(f"    Rendered: {messages[0]['content'].get('text')}")
                    else:
                        print(f"    RPC Error: {result.get('error')}")
            else:
                print("    Warning: welcome-prompt not found in registry.")
    except Exception as e:
        print(f"    Prompt Error: {e}")

    print("\n=== Scenario Verification Complete ===")

if __name__ == "__main__":
    test_scenarios()
