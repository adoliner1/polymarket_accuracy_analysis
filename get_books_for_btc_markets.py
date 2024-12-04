import os
from dotenv import load_dotenv
from py_clob_client.constants import POLYGON
from py_clob_client.client import ClobClient
from py_clob_client.exceptions import PolyApiException
import json
from pprint import pprint

load_dotenv()

def print_market_and_book(market, token_books, f):
    # Print market question and basic info
    f.write(f"Question: {market.get('question', 'N/A')}\n")
    f.write(f"Condition ID: {market.get('condition_id', 'N/A')}\n")
    f.write(f"End Date: {market.get('end_date_iso', 'N/A')}\n\n")
    
    # Print order books for each token
    f.write("Order Books:\n")
    for token in market.get('tokens', []):
        token_id = token.get('token_id')
        outcome = token.get('outcome')
        if token_id in token_books:
            f.write(f"\nOutcome: {outcome}\n")
            f.write(f"Token ID: {token_id}\n")
            book = token_books[token_id]
            for key, value in book.items():
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

def is_btc_market(question):
    if not question:
        return False
    question = question.lower()
    return 'btc' in question or 'bitcoin' in question

# Setup CLOB client
host = "https://clob.polymarket.com"
key = os.getenv("PK")
chain_id = POLYGON
clob_client = ClobClient(host, key=key, chain_id=chain_id)
clob_client.set_api_creds(clob_client.create_or_derive_api_creds())

with open('btc_markets_and_books.txt', 'w') as f:
    markets = get_all_markets(clob_client)
    f.write(f"Total markets fetched: {len(markets)}\n\n")
    
    btc_markets_checked = 0
    books_found = 0
    
    for market in markets:
        if market.get('closed') and is_btc_market(market.get('question')):
            btc_markets_checked += 1
            print(f"\nChecking market: {market.get('question')}")
            
            token_books = {}
            for token in market.get('tokens', []):
                token_id = token.get('token_id')
                if token_id:
                    try:
                        print(f"Trying to get order book for outcome '{token.get('outcome')}' with token ID: {token_id}")
                        book = clob_client.get_order_book(str(token_id))
                        if book:
                            token_books[token_id] = book
                            books_found += 1
                    except PolyApiException as e:
                        print(f"\nDetailed error for token {token_id}:")
                        print(f"Status code: {e.status_code}")
                        print(f"Error message: {e.error_msg}")
                        print(f"Full exception: {str(e)}")
                        continue
            
            if token_books:  # Only print if we got any order book data
                print_market_and_book(market, token_books, f)
                
    print(f"\nProcessing complete:")
    print(f"Total BTC markets checked: {btc_markets_checked}")
    print(f"Total order books found: {books_found}")