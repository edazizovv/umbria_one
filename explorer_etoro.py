#
import os
import uuid
import requests

#
from dotenv import load_dotenv
import pandas

#


#
load_dotenv()

url = "https://public-api.etoro.com/api/v1/market-data/search"

headers = {
    "x-api-key": os.environ.get("API_KEY"),
    "x-user-key": os.environ.get("USER_KEY"),
    "x-request-id": str(uuid.uuid4()),
}

symbol = "AAPL"
params = {
    "internalSymbolFull": symbol,
}

response = requests.get(url, headers=headers, params=params)

instrument = None
if response.status_code == 200:
    data = response.json()

    instrument = next((item for item in data['items'] if item['internalSymbolFull'] == symbol), None)

    if instrument:
        print(f"Instrument ID: {instrument['instrumentId']}")
    else:
        print("Instrument not found")
else:
    print(f"Error: {response.status_code}")


if instrument is None:
    raise Exception("Instrument not found")

# historical OHLC candles

direction = "desc"
interval = "OneMinute"
candlesCount = 1000
instrumentId = instrument['instrumentId']

url = f"https://public-api.etoro.com/api/v1/market-data/instruments/{instrumentId}/history/candles/{direction}/{interval}/{candlesCount}"

headers = {
    "x-api-key": os.environ.get("API_KEY"),
    "x-user-key": os.environ.get("USER_KEY"),
    "x-request-id": str(uuid.uuid4()),
}

params = {
}

response = requests.get(url, headers=headers, params=params)

data_candles = None
if response.status_code == 200:
    data_candles = response.json()

else:
    print(f"Error: {response.status_code}")

if data_candles:
    items = ["instrumentID", "fromDate", "open", "high", "low", "close", "volume"]
    new_data_candles = {}
    for item in items:
        new_data_candles[item] = [x[item] for x in data_candles["candles"][0]["candles"]]
    new_data_candles = pandas.DataFrame(new_data_candles)


# current market rates

direction = "desc"
interval = "OneMinute"
candlesCount = 1000
instrumentId = instrument['instrumentId']

url = f"https://public-api.etoro.com/api/v1/market-data/instruments/rates"

headers = {
    "x-api-key": os.environ.get("API_KEY"),
    "x-user-key": os.environ.get("USER_KEY"),
    "x-request-id": str(uuid.uuid4()),
}

params = {
    "instrumentIds": instrument['instrumentId'],
}

response = requests.get(url, headers=headers, params=params)

data_rates = None
if response.status_code == 200:
    data_rates = response.json()

else:
    print(f"Error: {response.status_code}")

if data_rates:
    data_rates_current_record = pandas.DataFrame(
        data={
            "instrumentID": [data_rates["rates"][0]["instrumentID"]],
            "ask": [data_rates["rates"][0]["ask"]],
            "bid": [data_rates["rates"][0]["bid"]],
            "date": [data_rates["rates"][0]["date"]],
        }
    )
