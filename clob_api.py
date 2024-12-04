import os
from dotenv import load_dotenv
from py_clob_client.constants import POLYGON
from py_clob_client.client import ClobClient
import json
from pprint import pprint
load_dotenv()
def print_market_fields(market, f):
   for key, value in market.items():
       f.write(f"{key}: {value}\n")
   f.write("-" * 80 + "\n")
def get_all_markets(client):
   all_markets = []
   cursor = ""
   
   while True:
       resp = client.get_markets(next_cursor=cursor)
       all_markets.extend(resp['data'])
       print(f"Fetched {len(resp['data'])} markets...")
       
       cursor = resp.get('next_cursor')
       if cursor == "LTE=":
           break
           
   return all_markets
host = "https://clob.polymarket.com"
key = os.getenv("PK")
chain_id = POLYGON
client = ClobClient(host, key=key, chain_id=chain_id)
client.set_api_creds(client.create_or_derive_api_creds())
with open('clob_market_data.txt', 'w') as f:
   markets = get_all_markets(client)
   f.write(f"Total markets fetched: {len(markets)}\n")
   for market in markets:
       print_market_fields(market, f)