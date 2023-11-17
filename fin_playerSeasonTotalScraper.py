import os
import aiohttp
import asyncio
import json
from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import OutputType
from bs4 import BeautifulSoup
from urllib.parse import quote
from aiohttp_socks import ProxyConnector

# Define the Oxylabs proxy URL
oxylabs_proxy_url = "socks5://customer-devnolant:Bingolucy1@pr.oxylabs.io:7777"

async def is_proxy_working(proxy):
    try:
        async with aiohttp.ClientSession(connector=ProxyConnector.from_url(proxy, rdns=True)) as session:
            async with session.get('https://www.basketball-reference.com', timeout=5) as response:
                return response.status == 200
    except Exception as e:
        return False

async def get_working_proxy(proxy_url):
    if await is_proxy_working(proxy_url):
        print(f"Working proxy found: {proxy_url}")
        return proxy_url
    raise Exception("No working proxy found")

# Set the Oxylabs proxy as an environment variable
os.environ['HTTP_PROXY'] = oxylabs_proxy_url
os.environ['HTTPS_PROXY'] = oxylabs_proxy_url

# Fetch the player season totals using Oxylabs proxy
year = 2024
json_file_path = f"./{year-1}_{year}_player_season_totals.json"

client.players_season_totals(
    season_end_year=year,
    output_type=OutputType.JSON,
    output_file_path=json_file_path
)

# Load the JSON data
with open(json_file_path, 'r') as file:
    players_data = json.load(file)

# Define a function to generate the GameLog URL
def generate_gamelog_url(player_slug, year):
    first_letter_of_last_name = player_slug[0]
    return f"https://www.basketball-reference.com/players/{first_letter_of_last_name}/{player_slug}/gamelog-advanced/{year}"

# Modify each player's dictionary to add the URL
for player in players_data:
    player_slug = player['slug']
    player['gamelog_url'] = generate_gamelog_url(player_slug, year)

# Save the modified data back to the JSON file
with open(json_file_path, 'w') as file:
    json.dump(players_data, file, indent=4)
