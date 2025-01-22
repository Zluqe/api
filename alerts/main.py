import requests
import yaml
import datetime

# 0 9,18 22-29 * * /usr/bin/python3 /path/script.py

with open("config.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

PTERO_PANEL_URL = cfg['panel']['panel_url']
API_KEY = cfg['panel']['api_key']
DISCORD_WEBHOOK_URL = cfg['discord']['webhook_url']

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
        response = requests.get(f"{PTERO_PANEL_URL}/api/application/servers", headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        return data['data']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching servers: {e}")
        return []

def get_server_details(server_id):
    """
    Fetches detailed information about a specific server.
    """
    try:
        response = requests.get(f"{PTERO_PANEL_URL}/api/application/servers/{server_id}", headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        return data['attributes']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for server {server_id}: {e}")
        return None

def get_user_details(user_id):
    """
    Fetches details for a specific user using their user ID.
    """
    try:
        response = requests.get(f"{PTERO_PANEL_URL}/api/application/users/{user_id}", headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        return data['attributes']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user details for user {user_id}: {e}")
        return None

def send_discord_notification(username, server_name, server_id):
    """
    Sends a ping notification and an embed to a Discord webhook.
    """
    try:
        server_url = f"{cfg['panel']['panel_url']}/server/{server_id}"
        
        ping_message = {
            "content": f"<@{username}> You have a server at risk of deletion!"
        }
        response_ping = requests.post(DISCORD_WEBHOOK_URL, json=ping_message)
        response_ping.raise_for_status()

        embed = {
            "title": "⚠️ Server Deletion Warning ⚠️",
            "description": f"<@{username}>, your server **[{server_name}]({server_url})** is suspended and at risk of deletion.",
            "color": 15158332,
            "fields": [
                {
                    "name": "Server Name",
                    "value": f"```{server_name}```",
                    "inline": True
                },
                {
                    "name": "Deletion Date",
                    "value": f"```30th of this month```",
                    "inline": True
                },
                {
                    "name": "Action Required",
                    "value": "```Please renew your server to avoid deletion. If you are unable to renew, please contact support.```",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Zluqe | Free Bot Hosting!",
                "icon_url": "https://raw.githubusercontent.com/Zluqe/logo/refs/heads/main/z.png"
            },
            "timestamp": f"{datetime.datetime.now().isoformat()}"
        }
        embed_message = {"embeds": [embed]}
        response_embed = requests.post(DISCORD_WEBHOOK_URL, json=embed_message)
        response_embed.raise_for_status()

        print(f"Ping and embed notification sent to Discord for user {username}.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Discord notifications: {e}")

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

    for s in suspended_servers:
        server_id = s['id']
        server_name = s['name']
        user_id = s.get('user')

        if not user_id:
            print(f"No user ID found for server {server_id} ({server_name}). Skipping notification.")
            continue

        user_details = get_user_details(user_id)
        if not user_details:
            print(f"Failed to retrieve details for user ID {user_id}. Skipping notification.")
            continue

        username = user_details.get('username')
        if not username:
            print(f"Username not found for user ID {user_id}. Skipping notification.")
            continue

        send_discord_notification(username, server_name, server_id)

if __name__ == "__main__":
    main()