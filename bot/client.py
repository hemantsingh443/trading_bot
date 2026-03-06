import os
import time
from dotenv import load_dotenv
from binance.client import Client

load_dotenv()

def get_client():
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    client = Client(api_key, api_secret, testnet=True)

    # fix timestamp drift
    client.timestamp_offset = client.get_server_time()['serverTime'] - int(time.time() * 1000)

    return client