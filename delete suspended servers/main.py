import requests
import yaml

# Load the configuration file
with open("./config.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

PTERO_PANEL_URL = cfg["panel"]["url"]
API_KEY = cfg["panel"]["api_key"]
GET_SERVERS_ENDPOINT = f"{PTERO_PANEL_URL}/api/application/servers"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def get_all_servers():
    """
    Fetches all servers from the Pterodactyl Panel using the Application API.
    """
    try:
        response = requests.get(GET_SERVERS_ENDPOINT, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        return data['data']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching servers: {e}")
        return []

def main():
    servers = get_all_servers()
    if not servers:
        print("No servers found or failed to retrieve servers.")
        return

    suspended_servers = []
    for server_wrapper in servers:
        server = server_wrapper['attributes']
        if server.get('suspended', False):
            suspended_servers.append(server)

    print(f"Found {len(suspended_servers)} suspended servers.")
    print("Performing a mock deletion (nothing will actually be deleted).")

    for s in suspended_servers:
        server_id = s['id']
        server_name = s['name']
        print(f"Mock deleting server ID {server_id}, Name: {server_name}")
        
        """
        delete_endpoint = f"{PTERO_PANEL_URL}/api/application/servers/{server_id}"
        try:
            delete_response = requests.delete(delete_endpoint, headers=HEADERS)
            delete_response.raise_for_status()
            print(f"Server {server_name} (ID: {server_id}) deleted successfully.")
        except requests.exceptions.RequestException as e:
            print(f"Error deleting server {server_name} (ID: {server_id}): {e}")
        """

if __name__ == "__main__":
    main()