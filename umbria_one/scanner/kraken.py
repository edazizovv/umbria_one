#
import json
import requests
import websockets

#
import numpy

#


#
def get_token_lvl2_orderbook(
    ticker: str,
) -> dict:

    url = "https://api.kraken.com/0/public/Depth"

    params = {
        "pair": f"{ticker}xUSD",
        "asset_class": "tokenized_asset",
        "count": 5,
    }

    try:

        response = requests.get(
            url,
            params=params,
        )
        data = response.json()

        if data.get("error"):
            print(f"Error from Kraken: {data['error']}")
            result = numpy.nan
        else:

            result = data["result"]
            result = result[f"{ticker}xUSD"]

    except Exception as e:
        print(e)
        result = numpy.nan

    return result


async def get_websockets_token_lvl2_orderbook_stream(
    ticker: str,
    stream_handler,
):

    uri = "wss://ws.kraken.com/v2"

    async with websockets.connect(uri) as ws:
        subscribe = {
            "method": "subscribe",
            "params": {
                "channel": "book",
                "symbol": [f"{ticker}x/USD"],
                "depth": 10,
                # "include_tokenized_assets": True,
            }
        }
        await ws.send(json.dumps(subscribe))

        while True:
            result = json.loads(await ws.recv())
            if ("data" in result) and ("channel" in result) and ("type" in result):
                if (result["channel"] == "book"):
                    print(result.keys())
                    if (result["type"] in ("snapshot", "update")):
                        await stream_handler(result["data"][0])


def get_reference_price(
    ticker: str,
) -> float:
    """
    Get market price for the given ticker that will serve as the reference price for the strategy.

    :param ticker: ticker symbol
    :return: reference price
    """

    url = "https://api.kraken.com/0/public/Ticker"

    params = {
        "pair": f"{ticker}xUSD",
        "asset_class": "tokenized_asset",
    }

    try:

        response = requests.get(
            url,
            params=params,
        )
        data = response.json()

        if data.get("error"):
            print(f"Error from Kraken: {data['error']}")
            ask_price = numpy.nan
        else:

            result = data["result"]
            pair_name = list(result.keys())[0]
            ticker = result[pair_name]

            ask_price = ticker["a"][0]  # a = Ask [price, whole lot volume, lot volume]

    except Exception as e:
        print(e)
        ask_price = numpy.nan

    return ask_price
