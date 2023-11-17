import aiohttp
import asyncio
import random
from aiohttp_socks import ProxyConnector
import json
import os,sys
import contextlib
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import quote

if not os.path.exists('players'):
    os.makedirs('players')

@contextlib.contextmanager
def suppress_asyncio_stderr():
    original_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')
    try:
        yield
    finally:
        sys.stderr.close()
        sys.stderr = original_stderr

# Function to get the list of proxies
async def get_proxies(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
            return [proxy.strip() for proxy in text.split('\n') if proxy.strip() and proxy.count(':') == 1]

async def create_session(proxy_ip, proxy_port):
    try:
        proxy_url = f"socks5://customer-devnolant:Bingolucy1@pr.oxylabs.io:7777"
        connector = ProxyConnector.from_url(proxy_url, rdns=True)
        return aiohttp.ClientSession(connector=connector)
    except Exception as e:
        print(f"Error creating session with proxy {proxy_ip}:{proxy_port}: {e}")
        return None

async def is_proxy_working(proxy_ip, proxy_port):
    session = await create_session(proxy_ip, proxy_port)
    if not session:
        return False
    try:
        async with session.get('https://www.basketball-reference.com', timeout=10) as response:
            return response.status == 200
    except Exception as e:
        print(f"Proxy {proxy_ip}:{proxy_port} failed with exception: {e.__class__.__name__}: {e}")
        return False
    finally:
        await session.close()

async def validate_proxies(proxies):
    tasks = [is_proxy_working(proxy.split(':')[0], proxy.split(':')[1]) for proxy in proxies]
    results = await asyncio.gather(*tasks)
    return [proxies[i] for i, valid in enumerate(results) if valid]

ua = UserAgent()
headers = {'User-Agent': ua.random}

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'id': 'pgl_advanced'})
    if table:
        headers = [th.getText() for th in table.find('thead').find_all('th')]
        headers = [th for th in headers if not th.startswith('Rk')]
        rows = table.find('tbody').find_all('tr')
        game_log_data = []
        for row in rows:
            if 'class' in row.attrs and 'thead' in row.attrs['class']:
                continue
            cols = row.find_all('td')
            row_data = {headers[i]: (cell.get_text().strip() or None) for i, cell in enumerate(cols)}
            game_log_data.append(row_data)
        return game_log_data
    else:
        print('Table not found.')
        return None

async def scrape_player_game_log(proxy, player):
    retry_count = 0
    max_retries = 3
    while retry_count < max_retries:
        try:
            proxy_ip, proxy_port = proxy.split(':')
            session = await create_session(proxy_ip, proxy_port)
            if session:
                async with session.get(player['gamelog_url'], headers=headers, timeout=20) as response:
                    if response.status in [429, 403]:
                        return "retry"
                    response.raise_for_status()
                    html = await response.text()
                    game_log_data = parse_html(html)
                if game_log_data:
                    encoded_player_name = quote(player['name'])
                    player_filename = f'players/{encoded_player_name}.json'
                    with open(player_filename, 'w', encoding='utf-8', errors='replace') as file:
                        json.dump({'original_data': player, 'gamelog_summary': game_log_data}, file, indent=4, ensure_ascii=False)
                    print(f"Data fetched for {encoded_player_name} :{proxy_ip}")
                    return None
        except Exception as e:
                print(f"An error occurred while processing {player['name']} with proxy {proxy}: {e}")
                retry_count += 1
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
        finally:
            await session.close()
        return "retry"  # If max retries reached

def combine_json_files(players_data, batch_size):
    json_files = [f'players/{quote(player["name"])}.json' for player in players_data]
    combined_data = []
    for file in json_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                player_data = json.load(f)
                player_data['original_data'].update({'gamelog_summary': player_data['gamelog_summary']})
                del player_data['gamelog_summary']  # Remove the gamelog_summary key at the root level
                combined_data.append(player_data['original_data'])  # Append the updated original_data

    combined_filename = 'combined_players_data.json'
    with open(combined_filename, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=4, ensure_ascii=False)


async def main(players_data, batch_size):
    proxy_list_url = 'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt'
    proxies = await get_proxies(proxy_list_url)
    working_proxies = await validate_proxies(proxies)
    if not working_proxies:
        print("No working proxies found. Exiting.")
        return

    players_queue = players_data.copy()
    processed_players = []  # Keep track of successfully processed players

    while players_queue:
        current_batch = players_queue[:batch_size]
        remaining_batch = current_batch.copy()

        while remaining_batch:
            for proxy in working_proxies:
                tasks = [asyncio.create_task(scrape_player_game_log(proxy, player)) for player in remaining_batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Update remaining_batch based on results
                new_remaining_batch = []
                for player, result in zip(remaining_batch, results):
                    if result == "retry":
                        print(f"Retrying {player['name']}")
                        new_remaining_batch.append(player)
                    else:
                        processed_players.append(player)
                        if len(processed_players) % 10 == 0:
                            combine_json_files(processed_players[-10:], batch_size)

                remaining_batch = new_remaining_batch

                if not remaining_batch:
                    break  # Move to the next batch if all players in the current batch are processed

        # Update the main queue
        players_queue = players_queue[len(current_batch):]

    # Save any remaining players at the end
        if processed_players:
            combine_json_files(processed_players, batch_size)


if __name__ == "__main__":
    with open('2023_2024_player_season_totals.json', 'r', encoding='utf-8') as file:
        players_data = json.load(file)
    batch_size = 10
    with suppress_asyncio_stderr():
        asyncio.get_event_loop().run_until_complete((main(players_data, batch_size)))
