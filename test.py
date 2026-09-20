import os
import requests
from dotenv import load_dotenv

load_dotenv()

# 1) configure these (in your .env):
#    HOME_ASSISTANT_MCP_URL=https://hass.rishilabs.online/mcp_server/sse
#    HOME_ASSISTANT_TOKEN=<your long-lived token>
#    HA_URL=https://hass.rishilabs.online    # your HA base URL
#    HA_TOKEN=<same long-lived token for REST calls>

MCP_URL = os.getenv("HOME_ASSISTANT_MCP_URL", "").strip()
MCP_TOKEN = os.getenv("HOME_ASSISTANT_TOKEN", "").strip()
HA_URL = os.getenv("HA_URL", "").strip()
HA_TOKEN = os.getenv("HA_TOKEN", "").strip()

print("MCP SSE URL =", MCP_URL)
print("HA REST URL =", HA_URL)
print("Token starts with:", HA_TOKEN[:8] if HA_TOKEN else "not set")

# 2) smoke-test the SSE endpoint
resp = requests.get(MCP_URL, headers={"Authorization": f"Bearer {MCP_TOKEN}"}, stream=True, timeout=10)
print(f"SSE HTTP status: {resp.status_code}")
if resp.status_code != 200:
    print(resp.text)
    exit(1)

# read and discard the first SSE event
for raw in resp.iter_lines():
    line = raw.decode("utf-8")
    if not line:
        break
    print("·", line)

# 3) now call HA's /api/states to get *all* entities
states_resp = requests.get(
    f"{HA_URL.rstrip('/')}/api/states",
    headers={
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    },
    timeout=10
)
if states_resp.status_code != 200:
    print("Failed to fetch states:", states_resp.status_code, states_resp.text)
    exit(1)

all_entities = states_resp.json()

# 4) filter only the lights and print their states
lights = [e for e in all_entities if e["entity_id"].startswith("light.")]
print(f"\nFound {len(lights)} light entities:")
for light in lights:
    eid = light["entity_id"]
    state = light["state"]
    name = light.get("attributes", {}).get("friendly_name", eid)
    print(f"- {eid} ({name}): {state}")
