import requests
import json
import time

# --- Configuration ---
BASE_URL = "http://localhost:4444"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "ContextForge#2026!"

def demonstrate():
    print("=== ContextForge Capability Demonstration ===")
    
    # 1. Authentication
    print("\n[1] Authenticating as Admin...")
    session = requests.Session()
    login_response = session.post(f"{BASE_URL}/auth/login", data={
        "username": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if login_response.status_code == 200:
        print("    Success: Secure Session Established.")
    else:
        print(f"    Failed: {login_response.text}")
        return

    # 2. Discovery: Gateways
    print("\n[2] Discovering Federated Gateways...")
    gateways = session.get(f"{BASE_URL}/gateways").json()
    print(f"    Found {len(gateways)} Federated MCP Servers:")
    for gw in gateways:
        print(f"    - {gw['name']} ({gw['url']})")

    # 3. Discovery: Unified Tool Catalog
    print("\n[3] Querying Trans-Gateway Tool Catalog...")
    tools = session.get(f"{BASE_URL}/tools").json()
    print(f"    {len(tools)} tools indexed across all federated peers.")
    # Show first few as example
    for tool in tools[:3]:
        print(f"    - Tool: {tool['name']} (Source: {tool['gateway_slug']})")

    # 4. Virtual Server Composition
    print("\n[4] Composition: Virtual Server Aggregation...")
    servers = session.get(f"{BASE_URL}/servers").json()
    for srv in servers:
        srv_details = session.get(f"{BASE_URL}/servers/{srv['id']}").json()
        tool_names = [t['name'] for t in srv_details.get('tools', [])]
        print(f"    - Virtual Server: '{srv['name']}'")
        print(f"      Bundling: {', '.join(tool_names[:3])}...")

    # 5. Governance: RBAC & Team Scoping
    print("\n[5] Governance: Checking Team-Based Access...")
    teams = session.get(f"{BASE_URL}/teams").json()
    print(f"    Managing {len(teams)} organizational teams.")
    for team in teams:
        print(f"    - {team['name']} (ID: {team['id'][:8]})")

    # 6. Observability: Live Traffic
    print("\n[6] Observability: Real-Time Traffic Metrics...")
    # Get overall stats
    metrics = session.get(f"{BASE_URL}/admin/overview/partial").text
    if "Total Invocations" in metrics:
        print("    Live metrics aggregation confirmed on Dashboard.")
    
    # Simulate a tool invocation check (Discovery check)
    print("\n[7] Protocol: MCP Schema Introspection...")
    if tools:
        test_tool = tools[0]
        print(f"    Introspecting {test_tool['name']}...")
        print(f"    Schema: {json.dumps(test_tool['input_schema'], indent=4)[:150]}...")

    print("\n=== Demonstration Script Complete ===")
    print(f"Live Dashboard available at: {BASE_URL}/admin")

if __name__ == "__main__":
    demonstrate()
