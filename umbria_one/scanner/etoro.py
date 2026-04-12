#
import requests
from typing import Union

#


#
from umbria_one.tech.connectors import EtoroConnector

#
def get_instrument_id(
    ec: EtoroConnector,
    ticker: str,
) -> Union[str, None]:

    url = f"{ec.base_url}/market-data/search?internalSymbolFull={ticker}"

    response = requests.get(
        url,
        headers=ec.headers,
    )

    result = None
    if response.status_code == 200:

        data = response.json()

        for instrument in data.get("items", []):
            if instrument["internalSymbolFull"] == ticker:
                result = instrument["instrumentId"]

    return result


def get_stock_orders(
    ec: EtoroConnector,
    ticker: str,
) -> dict:

    instrument_id = get_instrument_id(
        ec=ec,
        ticker=ticker,
    )
    if not instrument_id:
        raise ValueError("ticker not found")

    url = f"{ec.base_url}/portfolio/orders"

    response = requests.get(
        url,
        headers=ec.headers,
    )

    if response.status_code == 200:

        all_orders = response.json().get("orders", [])

        ticker_orders = [o for o in all_orders if o.get("instrumentId") == instrument_id]
        return ticker_orders

    else:
        print(f"Error fetching orders: {response.text}")
        return []
