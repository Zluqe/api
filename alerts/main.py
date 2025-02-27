import aiohttp
import asyncio
import yaml
import datetime
import calendar

# Load the configuration file
with open("./config.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

def get_last_day_of_current_month():
    today = datetime.date.today()
    year = today.year
    month = today.month
    last_day = calendar.monthrange(year, month)[1]
    return datetime.date(year, month, last_day)

last_day_date = get_last_day_of_current_month()

# Configuration values
PTERO_PANEL_URL = cfg['panel']['panel_url']
API_KEY = cfg['panel']['api_key']
DISCORD_WEBHOOK_URL = cfg['discord']['webhook_url']

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

async def fetch(session, url):
    """
    Asynchronously fetch data from the given URL.
    """
    try:
        async with session.get(url, headers=HEADERS) as response:
            response.raise_for_status()
            return await response.json()
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return None

async def send_discord_notification(session, username, server_name, server_uuid):
    """
    Sends a ping notification and an embed to a Discord webhook.
    """
    try:
        server_url = f"{cfg['panel']['panel_url']}/server/{server_uuid}"
        
        # Ping message
        ping_message = {
            "content": f"⚠️ <@{username}> You have a server at risk of deletion! ⚠️"
        }
        async with session.post(DISCORD_WEBHOOK_URL, json=ping_message) as ping_response:
            ping_response.raise_for_status()

        # Embed message
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
                    "value": f"```{last_day_date}```",
                    "inline": True
                },
                {
                    "name": "Action Required",
                    "value": "```Please renew your server, or resolve any issues by opening a ticket!```",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Zluqe | Quality Hosting, for Quality Bots!",
                "icon_url": "https://raw.githubusercontent.com/Zluqe/logo/refs/heads/main/z.png"
            },
            "timestamp": f"{datetime.datetime.now().isoformat()}",
        }
        embed_message = {"embeds": [embed]}  # Embeds are sent as a list
        async with session.post(DISCORD_WEBHOOK_URL, json=embed_message) as embed_response:
            embed_response.raise_for_status()

        print(f"Ping and embed notification sent to Discord for user {username}.")
    except Exception as e:
        print(f"Error sending Discord notifications: {e}")

async def process_server(session, server):
    """
    Process an individual server, fetching user details and sending notifications.
    """
    server_uuid = server['uuid']  # Use the UUID for the server URL
    server_name = server['name']
    user_id = server.get('user')  # Extract user ID (this is the username in the panel)

    if not user_id:
        print(f"No user ID found for server {server_uuid} ({server_name}). Skipping notification.")
        return

    # Fetch user details to get the username
    user_details_url = f"{PTERO_PANEL_URL}/api/application/users/{user_id}"
    user_details = await fetch(session, user_details_url)
    if not user_details:
        print(f"Failed to retrieve details for user ID {user_id}. Skipping notification.")
        return

    username = user_details.get('attributes', {}).get('username')
    if not username:
        print(f"Username not found for user ID {user_id}. Skipping notification.")
        return

    # Send the notification with ping and embed
    await send_discord_notification(session, username, server_name, server_uuid)

async def main():
    """
    Main asynchronous function to fetch servers and process notifications sequentially with delays.
    """
    async with aiohttp.ClientSession() as session:
        servers_url = f"{PTERO_PANEL_URL}/api/application/servers"
        servers_data = await fetch(session, servers_url)
        if not servers_data or 'data' not in servers_data:
            print("No servers found or failed to retrieve servers.")
            return

        servers = [server['attributes'] for server in servers_data['data'] if server['attributes'].get('suspended', False)]

        print(f"Found {len(servers)} suspended servers.")

        for server in servers:
            await process_server(session, server)  # Process each server
            await asyncio.sleep(2)  # Wait 2 seconds between each notification

if __name__ == "__main__":
    asyncio.run(main())
