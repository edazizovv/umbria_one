#
import requests

#
import numpy

#


#
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
