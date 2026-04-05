#
import datetime
import requests
from typing import Union

#
import pandas

#


#
def get_historical_ohlc(
    ticker: str,
    interval: int,
    since: Union[datetime, None] = None,
) -> tuple[pandas.DataFrame, dict, str]:
    """

    :param ticker:
    :param interval:
    :param since:
    :return:
    """

    url = "https://api.kraken.com/0/public/OHLC"

    params = {
        "pair": f"{ticker}xUSD",
        "interval": interval,
        "asset_class": "tokenized_asset",
    }

    # Kraken does not have "end_date",
    # it only returns 720 most recent date snapshots after 'since' date
    if since:
        params["since"] = since

    try:

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("error"):
            data = pandas.DataFrame()
            error_data = data["error"]
            result_message = "api_error"
            return data, error_data, result_message

        data = pandas.DataFrame(
            data=data["result"][f"{ticker}xUSD"],
            columns=[
                "datetime",
                "open",
                "high",
                "low",
                "close",
                "vwap",
                "volume",
                "count",
            ],
        )

        data["datetime"] = pandas.to_datetime(data["datetime"], unit="s", utc=True).astype("datetime64[us, UTC]")
        data = data.set_index("datetime")

        float_columns = [
                "open",
                "high",
                "low",
                "close",
                "vwap",
                "volume",
        ]
        data[float_columns] = data[float_columns].astype(float)
        data["count"] = data["count"].astype(int)

        error_data = {}
        result_message = "ok"

        return data, error_data, result_message

    except Exception as e:

        data = pandas.DataFrame()
        error_data = {"exception": str(e)}
        result_message = "exception"

        return data, error_data, result_message
