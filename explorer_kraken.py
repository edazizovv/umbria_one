import requests

# 1. Define the API endpoint
url = "https://api.kraken.com/0/public/Ticker"

# 2. Set the parameters
# Use 'x' suffix for stocks (e.g., AAPLxUSD)
# 'asset_class' MUST be 'tokenized_asset' for xStocks
params = {
    "pair": "AAPLxUSD",
    "asset_class": "tokenized_asset"
}

try:
    # 3. Send the GET request
    response = requests.get(url, params=params)
    data = response.json()

    # 4. Handle errors and parse data
    if data.get("error"):
        print(f"Error from Kraken: {data['error']}")
    else:
        # Kraken returns data inside a 'result' object keyed by the pair name
        result = data["result"]
        pair_name = list(result.keys())[0]
        ticker = result[pair_name]

        # Extract specific price data
        last_price = ticker["c"][0]  # c = Last trade closed [price, lot volume]
        ask_price = ticker["a"][0]   # a = Ask [price, whole lot volume, lot volume]
        bid_price = ticker["b"][0]   # b = Bid [price, whole lot volume, lot volume]

        print(f"--- {pair_name} ---")
        print(f"Last Price: {last_price}")
        print(f"Ask Price:  {ask_price}")
        print(f"Bid Price:  {bid_price}")

except Exception as e:
    print(f"An error occurred: {e}")


# DECIDE, THEN EXECUTE

import time
import requests
import urllib.parse
import hashlib
import hmac
import base64

# --- Configuration ---
API_KEY = 'YOUR_API_KEY'
API_SECRET = 'YOUR_API_SECRET'
BASE_URL = "https://api.kraken.com"


def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    return base64.b64encode(mac.digest()).decode()


def place_xstock_limit_order(pair, volume, price, order_type='buy'):
    urlpath = '/0/private/AddOrder'

    data = {
        "nonce": str(int(time.time() * 1000)),
        "pair": pair,
        "type": order_type,
        "ordertype": "limit",  # Changed to limit
        "price": price,  # REQUIRED for limit orders
        "volume": volume,
        "asset_class": "tokenized_asset"
    }

    headers = {
        "API-Key": API_KEY,
        "API-Sign": get_kraken_signature(urlpath, data, API_SECRET)
    }

    response = requests.post(BASE_URL + urlpath, headers=headers, data=data)
    return response.json()


# Execute: Buy 1 AAPLx share only if the price is $180.50 or lower
result = place_xstock_limit_order("AAPLxUSD", 1, 180.50)
print(result)
