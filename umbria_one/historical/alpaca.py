#
import datetime
from typing import Union

#
import numpy
import pandas
from pandas.tseries.offsets import BusinessDay
from alpaca.data.requests import StockBarsRequest, OptionBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.enums import ContractType

#
from umbria_one.tech.connectors import AlpacaConnector
from umbria_one.tech.utils import strike_step_heuristic, build_option_symbol

#
def get_historical_stock_ohlc(
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


def get_historical_option_ohlc(
    ac: AlpacaConnector,
    ticker: str,
    interval: TimeFrame,
    interval_datetime_delta: datetime.timedelta,
    min_expiration_date: datetime.datetime,
    max_strike: float,
    contract_type: str,
    snapshot_date: datetime.datetime,
) -> dict:

        symbol = build_option_symbol(
            underlying=ticker,
            expiration=min_expiration_date,
            strike=max_strike,
            option_type=contract_type,
        )

        request = OptionBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=interval,
            start=snapshot_date,
            end=snapshot_date + interval_datetime_delta,
        )

        result_bars = ac.data.options.get_option_bars(request)

        if len(result_bars.data) == 0:

            option_results = {
                "option_close": numpy.nan,
                "option_high": numpy.nan,
                "option_low": numpy.nan,
                "option_open": numpy.nan,
                "option_trade_count": numpy.nan,
                "option_volume": numpy.nan,
                "option_vwap": numpy.nan,
            }

        else:

            selection = [c for c in result_bars.data[symbol] if c.timestamp == snapshot_date]

            if len(selection) == 0:

                option_results = {
                    "option_close": numpy.nan,
                    "option_high": numpy.nan,
                    "option_low": numpy.nan,
                    "option_open": numpy.nan,
                    "option_trade_count": numpy.nan,
                    "option_volume": numpy.nan,
                    "option_vwap": numpy.nan,
                }

            else:

                selection = selection[0]

                option_results = {
                    "option_close": selection.close,
                    "option_high": selection.high,
                    "option_low": selection.low,
                    "option_open": selection.open,
                    "option_trade_count": selection.trade_count,
                    "option_volume": selection.volume,
                    "option_vwap": selection.vwap,
                }

        return option_results


def get_mass_load_option_dynamics(
    ac: AlpacaConnector,
    ticker: str,
    interval: TimeFrame,
    interval_datetime_delta: datetime.timedelta,
    data_historical_stock_ohlc_df: pandas.DataFrame,
) -> pandas.DataFrame:

    data_historical_stock_ohlc_df["min_expiration_date"] = (
        (data_historical_stock_ohlc_df.index.to_series() + pandas.offsets.BDay(4) + pandas.offsets.Week(weekday=4)).dt.date
    )

    data_historical_stock_ohlc_df["_strike_step"] = (
        data_historical_stock_ohlc_df["close"]
        .apply(
            func=lambda x: strike_step_heuristic(spot=x)
        )
    )
    data_historical_stock_ohlc_df["max_strike_price"] = (
        data_historical_stock_ohlc_df["_strike_step"] * (
            data_historical_stock_ohlc_df["close"] // data_historical_stock_ohlc_df["_strike_step"]
        ).astype(int)
    )

    allocate_cols = [
        "option_close",
        "option_high",
        "option_low",
        "option_open",
        "option_trade_count",
        "option_volume",
        "option_vwap",
    ]

    data_historical_stock_ohlc_df["timestamp"] = (
        data_historical_stock_ohlc_df.index.to_series()
    )

    data_historical_stock_ohlc_df[
        allocate_cols
    ] = (
        data_historical_stock_ohlc_df
        .apply(
            func=lambda x: get_historical_option_ohlc(
                ac=ac,
                ticker=ticker,
                interval=interval,
                interval_datetime_delta=interval_datetime_delta,
                min_expiration_date=x["min_expiration_date"],
                max_strike=x["max_strike_price"],
                contract_type="P",
                snapshot_date=x["timestamp"],
            ),
            axis=1,
            result_type="expand",
        )
    )

    data_historical_stock_ohlc_df = (
        data_historical_stock_ohlc_df
        .rename(
            columns={
                c: f"put_{c}"
                for c in allocate_cols
            }
        )
    )

    data_historical_stock_ohlc_df[
        allocate_cols
    ] = (
        data_historical_stock_ohlc_df
        .apply(
            func=lambda x: get_historical_option_ohlc(
                ac=ac,
                ticker=ticker,
                interval=interval,
                interval_datetime_delta=interval_datetime_delta,
                min_expiration_date=x["min_expiration_date"],
                max_strike=x["max_strike_price"],
                contract_type="C",
                snapshot_date=x["timestamp"],
            ),
            axis=1,
            result_type="expand",
        )
    )

    data_historical_stock_ohlc_df = (
        data_historical_stock_ohlc_df
        .rename(
            columns={
                c: f"call_{c}"
                for c in allocate_cols
            }
        )
    )

    data_historical_stock_ohlc_df = (
        data_historical_stock_ohlc_df
        .drop(columns=["timestamp"])
    )

    return data_historical_stock_ohlc_df
