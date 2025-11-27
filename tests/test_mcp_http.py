import requests
import json
from sseclient import SSEClient

# 1. Connect to SSE endpoint to get session ID
sse_url = "http://localhost:5000/gradio_api/mcp/sse"
messages_url = "http://localhost:5000/gradio_api/mcp/messages/"

print(f"Connecting to {sse_url}...")
response = requests.get(sse_url, stream=True)
client = SSEClient(response)

session_id = None
for event in client.events():
    if event.event == "endpoint":
        # Extract session_id from URL: /gradio_api/mcp/messages/?session_id=...
        session_id = event.data.split("session_id=")[1]
        print(f"✅ Got Session ID: {session_id}")
        break

if not session_id:
    print("❌ Failed to get session ID")
    exit(1)

# 2. Send JSON-RPC request to call 'get_active_task'
rpc_payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "get_active_task",
        "arguments": {}
    }
}

full_url = f"{messages_url}?session_id={session_id}"
print(f"Sending request to {full_url}...")
print(f"Payload: {json.dumps(rpc_payload, indent=2)}")

resp = requests.post(full_url, json=rpc_payload)
print(f"Response Status: {resp.status_code}")
print(f"Response Body: {resp.text}")
