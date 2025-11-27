import requests
import json
import time
import sys
import threading

# Configuration
BASE_URL = "http://127.0.0.1:5000/gradio_api/mcp"
SSE_URL = f"{BASE_URL}/sse"
MESSAGES_URL = f"{BASE_URL}/messages/"

class MCPTester:
    def __init__(self):
        self.session_id = None
        self.running = True
        self.responses = {}
        self.lock = threading.Lock()

    def listen_sse(self):
        """Listen to SSE stream in a background thread."""
        try:
            with requests.get(SSE_URL, stream=True, timeout=None) as response:
                for line in response.iter_lines():
                    if not self.running:
                        break
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data: '):
                            data_content = decoded_line[6:]

                            # Check for session ID
                            if "session_id=" in data_content and not self.session_id:
                                self.session_id = data_content.split("session_id=")[1]
                                print(f"✅ Session ID established: {self.session_id}")
                                continue

                            # Check for JSON-RPC responses
                            try:
                                data = json.loads(data_content)
                                if "id" in data:
                                    with self.lock:
                                        self.responses[data["id"]] = data
                                        print(f"📩 Received Response for ID {data['id']}")
                            except:
                                pass
        except Exception as e:
            print(f"❌ SSE Listener Error: {e}")

    def call_tool(self, name, args={}):
        if not self.session_id:
            print("❌ No session ID yet")
            return False

        req_id = int(time.time() * 1000)
        rpc_url = f"{MESSAGES_URL}?session_id={self.session_id}"
        payload = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": args
            }
        }

        print(f"\n📤 Calling Tool: {name} (ID: {req_id})")
        requests.post(rpc_url, json=payload)

        # Wait for response
        start_time = time.time()
        while time.time() - start_time < 5:
            with self.lock:
                if req_id in self.responses:
                    result = self.responses[req_id]
                    print(json.dumps(result, indent=2))
                    return True
            time.sleep(0.1)

        print("❌ Timeout waiting for response")
        return False

    def run(self):
        print(f"🚀 Starting MCP Test Flow...")

        # Start listener thread
        t = threading.Thread(target=self.listen_sse)
        t.daemon = True
        t.start()

        # Wait for session ID
        print("⏳ Waiting for connection...")
        for _ in range(50):
            if self.session_id:
                break
            time.sleep(0.1)

        if not self.session_id:
            print("❌ Failed to connect")
            return False

        # Run Tests
        success = True

        # 1. Get Active Task
        if not self.call_tool("get_current_task"): success = False

        # 2. Add Task
        if not self.call_tool("add_task", {"title": "MCP Async Test", "description": "Testing async flow", "estimated_duration": "10 min"}): success = False

        # 3. Get Stats
        if not self.call_tool("get_productivity_stats"): success = False

        self.running = False
        return success

if __name__ == "__main__":
    tester = MCPTester()
    success = tester.run()
    sys.exit(0 if success else 1)
