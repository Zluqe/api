import requests
import yaml

# Load configuration
with open("../config.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

PTERO_PANEL_URL = cfg["panel"]["url"]
API_KEY = cfg["panel"]["api_key"]
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "Application/vnd.pterodactyl.v1+json",
    "Content-Type": "application/json",
}

def get_all_servers():
    url = f"{PTERO_PANEL_URL}/api/application/servers"
    all_servers = []
    while url:
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        body = resp.json()
        all_servers.extend(body.get("data", []))
        pagination = body.get("meta", {}).get("pagination", {})
        url = pagination.get("links", {}).get("next")

    return all_servers

def main():
    servers = get_all_servers()
    if not servers:
        print("No servers found or failed to retrieve servers.")
        return
    suspended = [
        item["attributes"] for item in servers
        if item["attributes"].get("suspended", False)
    ]
    print(f"Found {len(suspended)} suspended servers.")

    # Delete suspended servers
    for server in suspended:
        server_id = server["id"]
        server_name = server["name"]
        delete_url = f"{PTERO_PANEL_URL}/api/application/servers/{server_id}"
        try:
            del_resp = requests.delete(delete_url, headers=HEADERS)
            del_resp.raise_for_status()
            print(f"Deleted {server_name} (ID: {server_id}).")
        except requests.exceptions.RequestException as e:
            print(f"Error deleting {server_name} (ID: {server_id}): {e}")

if __name__ == "__main__":
    main()
