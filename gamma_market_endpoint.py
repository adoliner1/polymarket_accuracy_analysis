import os
import requests
from dotenv import load_dotenv
import json
from pprint import pprint
import time

load_dotenv()

def print_fields(item, f):
    for key, value in item.items():
        f.write(f"{key}: {value}\n")
    f.write("-" * 80 + "\n")

def get_all_items(endpoint, limit=500):
    url = f"https://gamma-api.polymarket.com/{endpoint}"
    params = {
        'limit': limit,
        'offset': 0,
        'closed': False,
        'order': 'createdAt',
        'ascending': True
    }
   
    all_items = []
    while True:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            items_data = response.json()
           
            if not items_data:
                break
               
            all_items.extend(items_data)
            print(f"Fetched {len(items_data)} {endpoint} from offset {params['offset']}")
           
            if len(items_data) < limit:
                break
               
            params['offset'] += limit
           
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {endpoint}: {e}")
            break
           
    print(f"Total {endpoint} fetched: {len(all_items)}")
    return all_items

def get_token_price_history(token_id):
    url = f"https://clob.polymarket.com/prices-history"
    params = {
        'market': token_id,
        'interval': '1m',
        'fidelity': 200
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching price history for token {token_id}: {e}")
        return None

# Fetch and save markets
with open('gamma_market_data.txt', 'w') as f:
    markets = get_all_items('markets')
    f.write(f"Total markets fetched: {len(markets)}\n")
    for market in markets:
        print_fields(market, f)

# Fetch and save events
with open('gamma_event_data.txt', 'w') as f:
    events = get_all_items('events')
    f.write(f"Total events fetched: {len(events)}\n")
    for event in events:
        print_fields(event, f)

# Fetch and save token price histories
with open('gamma_token_prices.txt', 'w') as f:
    token_count = 0
    for market in markets:
        if 'clobTokenIds' in market:
            f.write(f"\nMarket: {market.get('question', 'Unknown')}\n")
            f.write("-" * 80 + "\n")
            
            try:
                # Parse the JSON string to get the token IDs
                token_ids = json.loads(market['clobTokenIds']) if isinstance(market['clobTokenIds'], str) else market['clobTokenIds']
                
                for token_id in token_ids:
                    print(f"Processing token: {token_id}")  # Debug print
                    f.write(f"Token ID: {token_id}\n")
                    price_history = get_token_price_history(token_id)
                    
                    if price_history:
                        f.write("Price History:\n")
                        json.dump(price_history, f, indent=2)
                        f.write("\n")
                        token_count += 1
                    
                    f.write("-" * 80 + "\n")
                    # Add a small delay to avoid overwhelming the API
                    time.sleep(0.1)
            
            except json.JSONDecodeError as e:
                print(f"Error parsing token IDs for market {market.get('question', 'Unknown')}: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error processing market {market.get('question', 'Unknown')}: {e}")
                continue

    f.write(f"\nTotal tokens processed: {token_count}\n")