#
import datetime
from typing import Union

#
import pandas
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

#
from umbria_one.tech.connectors import AlpacaConnector

#
def get_historical_ohlc(
    ac: AlpacaConnector,
    ticker: str,
    interval: TimeFrame,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
) -> pandas.DataFrame:
    """

    :param ac:
    :param ticker:
    :param interval:
    :param start_date:
    :param end_date:
    :return:
    """

    historical_request = StockBarsRequest(
        symbol_or_symbols=ticker,
        timeframe=interval,
        start=start_date,
        end=end_date,
    )
    historical_bars = ac.data.stocks.get_stock_bars(historical_request)
    historical_data = historical_bars.df
    historical_data.index = historical_data.index.droplevel('symbol')

    return historical_data
