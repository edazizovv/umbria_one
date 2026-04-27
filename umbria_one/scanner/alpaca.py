#
import asyncio
import datetime
from functools import partial

#
import pandas
from alpaca.data.requests import StockLatestTradeRequest, OptionLatestTradeRequest, OptionLatestQuoteRequest
from alpaca.trading.requests import GetOptionContractsRequest
from alpaca.trading.enums import AssetStatus, ContractType, ExerciseStyle

#
from umbria_one.tech.utils import date_diff
from umbria_one.tech.connectors import AlpacaConnector

#
def get_market_price(
    ac: AlpacaConnector,
    ticker: str,
) -> float:
    """
    Retrieve market prices for a given ticker.

    :param ac: initialized alpaca connector
    :param ticker: ticker symbol
    :return: market price
    """

    trade_request = StockLatestTradeRequest(symbol_or_symbols=ticker)
    latest_trade = ac.data.stocks.get_stock_latest_trade(trade_request)
    market_price = latest_trade[ticker].price

    return market_price


def get_stocks_lvl1_orderbook(
    ac: AlpacaConnector,
    ticker: str,
) -> dict:

    trade_request = StockLatestTradeRequest(symbol_or_symbols=ticker)
    current_orderbook = ac.data.stocks.get_stock_latest_quote(trade_request)
    stock_orderbook = current_orderbook[ticker]

    return stock_orderbook


async def get_websockets_stocks_lvl1_orderbook_stream(
    ac: AlpacaConnector,
    ticker: str,
    stream_handler,
):

    bound_handler = partial(stream_handler, ticker=ticker)
    ac.data_live.subscribe_quotes(bound_handler, ticker)

    await ac.data_live._run_forever()


async def get_rest_portfolio_state(
    ac: AlpacaConnector,
    stream_handler,
):
    while True:
        positions = await asyncio.to_thread(ac.trading.get_all_positions)

        await stream_handler(positions=positions)

        await asyncio.sleep(5)


async def get_rest_current_orders(
    ac: AlpacaConnector,
    stream_handler,
):
    while True:
        orders = await asyncio.to_thread(ac.trading.get_orders)

        await stream_handler(orders=orders)

        await asyncio.sleep(5)


def get_options(
    ac: AlpacaConnector,
    ticker: str,
    reference_price: float,
    reference_date: datetime.date,
) -> dict:
    """
    Retrieve available options for a given ticker and market price.

    :param ac: initialized alpaca connector
    :param ticker: ticker symbol
    :param reference_price: reference price
    :param reference_date: reference date in YYYYMMDD format
    :return: options dictionary
    """

    # query / take the closest expiration that is not less than 4 days
    reference_4day = reference_date + datetime.timedelta(days=4)

    options_request = GetOptionContractsRequest(
        underlying_symbols=[ticker],
        status=AssetStatus.ACTIVE,
        type=ContractType.PUT,
        style=ExerciseStyle.AMERICAN,
        expiration_date_gte=reference_4day,
    )

    option_contracts = ac.trading.get_option_contracts(options_request)

    options_df = pandas.DataFrame(
        data=[
            {
                "expiration_date": c.expiration_date,
                "strike_price": c.strike_price,
                "symbol": c.symbol,
                "underlying_symbol": c.underlying_symbol,
                "selection_close_price": c.close_price,
                "selection_close_price_date": c.close_price_date,
            }
            for c in option_contracts.option_contracts
        ],
    )

    # take the closest expiration that is not less than 4 days
    target_expiration = options_df["expiration_date"].min()

    selected_options_df = options_df[
        (options_df["expiration_date"] == target_expiration)
    ].copy()

    # take strikes that are closest to the reference price
    lower_strike = selected_options_df.loc[(selected_options_df["strike_price"] <= reference_price), "strike_price"].max()
    upper_strike = selected_options_df.loc[(selected_options_df["strike_price"] >= reference_price), "strike_price"].min()
    if pandas.isna(lower_strike) and ~pandas.isna(upper_strike):
        strikes = [upper_strike]
    elif ~pandas.isna(lower_strike) and pandas.isna(upper_strike):
        strikes = [lower_strike]
    elif lower_strike == upper_strike:
        strikes = [lower_strike]
    else:
        strikes = [lower_strike, upper_strike]

    selected_options_df = selected_options_df[
        (selected_options_df["strike_price"].isin(strikes))
    ].copy()

    selected_options_ls = selected_options_df["symbol"].tolist()
    selected_options_df = selected_options_df.set_index("symbol")

    # request latest trades
    request_params = OptionLatestTradeRequest(symbol_or_symbols=selected_options_ls)
    latest_option_closes = ac.data.options.get_option_latest_trade(request_params)

    option_closes_df = pandas.DataFrame(
        data=[
            {
                "close_conditions": c.conditions,
                "close_exchange": c.exchange,
                "close_price": c.price,
                "close_size": c.size,
                "symbol": c.symbol,
                "close_tape": c.tape,
                "close_timestamp": c.timestamp,
            }
            for c in latest_option_closes.values()
        ],
    ).set_index("symbol")

    # request latest asks
    request_params = OptionLatestQuoteRequest(symbol_or_symbols=selected_options_ls)
    latest_option_asks = ac.data.options.get_option_latest_quote(request_params)

    option_asks_df = pandas.DataFrame(
        data=[
            {
                "ask_exchange": c.ask_exchange,
                "ask_price": c.ask_price,
                "ask_size": c.ask_size,
                "ask_conditions": c.conditions,
                "symbol": c.symbol,
                "ask_tape": c.tape,
                "ask_timestamp": c.timestamp,
            }
            for c in latest_option_asks.values()
        ],
    ).set_index("symbol")

    # map the prices
    result_df = selected_options_df.merge(
        right=option_closes_df,
        left_index=True,
        right_index=True,
    ).merge(
        right=option_asks_df,
        left_index=True,
        right_index=True,
    ).reset_index()

    #
    return result_df
