import requests
import json
import time
import sys
import threading

# Configuration
BASE_URL = "http://127.0.0.1:5000/gradio_api/mcp"
SSE_URL = f"{BASE_URL}/sse"
MESSAGES_URL = f"{BASE_URL}/messages/"

class MCPDebugger:
    def __init__(self):
        self.session_id = None
        self.running = True
        self.responses = {}
        self.lock = threading.Lock()

    def listen_sse(self):
        try:
            with requests.get(SSE_URL, stream=True, timeout=None) as response:
                for line in response.iter_lines():
                    if not self.running: break
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data: '):
                            data_content = decoded_line[6:]
                            if "session_id=" in data_content and not self.session_id:
                                self.session_id = data_content.split("session_id=")[1]
                                print(f"✅ Session ID: {self.session_id}")
                                continue
                            try:
                                data = json.loads(data_content)
                                if "id" in data:
                                    with self.lock:
                                        self.responses[data["id"]] = data
                                        print(f"📩 Response for {data['id']}")
                            except: pass
        except Exception as e: print(f"❌ SSE Error: {e}")

    def send_rpc(self, method, params=None):
        if not self.session_id: return False
        req_id = int(time.time() * 1000)
        rpc_url = f"{MESSAGES_URL}?session_id={self.session_id}"
        payload = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params is not None:
            payload["params"] = params

        print(f"\n📤 Sending {method} (ID: {req_id}) Params: {params}")
        requests.post(rpc_url, json=payload)

        start = time.time()
        while time.time() - start < 5:
            with self.lock:
                if req_id in self.responses:
                    print(json.dumps(self.responses[req_id], indent=2))
                    return True
            time.sleep(0.1)
        print("❌ Timeout")
        return False

    def run(self):
        t = threading.Thread(target=self.listen_sse); t.daemon = True; t.start()
        while not self.session_id: time.sleep(0.1)

        # 0. Initialize
        init_params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "TestClient", "version": "1.0"}
        }
        self.send_rpc("initialize", init_params)

        # 0.5 Initialized notification
        self.send_rpc("notifications/initialized", None)

        # 1. List Tools (no params)
        self.send_rpc("tools/list", None)

        # 2. Try calling get_current_task
        self.send_rpc("tools/call", {"name": "get_current_task", "arguments": {}})

        self.running = False
        return True

if __name__ == "__main__":
    MCPDebugger().run()
