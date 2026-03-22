#
import os

#
import pandas
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient, OptionHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest, OptionLatestTradeRequest, OptionLatestQuoteRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOptionContractsRequest
from alpaca.trading.enums import AssetStatus, ContractType

#


#
load_dotenv()

API_KEY = os.environ.get("ALPACA_API_KEY")
SECRET_KEY = os.environ.get("ALPACA_USER_KEY")

# StockHistoricalDataClient is used for market prices
# TradingClient is used to query the option chain (contracts)
data_stock_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
data_option_client = OptionHistoricalDataClient(API_KEY, SECRET_KEY)
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=False)


def get_market(ticker):

    # StockLatestTradeRequest fetches the most recent execution price
    trade_request = StockLatestTradeRequest(symbol_or_symbols=ticker)
    latest_trade = data_stock_client.get_stock_latest_trade(trade_request)
    current_price = latest_trade[ticker].price

    return current_price


def get_puts(ticker):

    # Filter for active contracts of type 'put' for the given underlying
    options_request = GetOptionContractsRequest(
        underlying_symbols=[ticker],
        status=AssetStatus.ACTIVE,
        type=ContractType.PUT
    )

    option_contracts = trading_client.get_option_contracts(options_request)

    return option_contracts


def get_puts_premiums_closes(symbols):

    request_params = OptionLatestTradeRequest(symbol_or_symbols=symbols)
    latest_trades = data_option_client.get_option_latest_trade(request_params)

    return latest_trades


def get_puts_premiums_asks(symbols):

    request_params = OptionLatestQuoteRequest(symbol_or_symbols=symbols)
    latest_quotes = data_option_client.get_option_latest_quote(request_params)

    return latest_quotes

current_price = get_market("AAPL")
option_contracts = get_puts("AAPL")

options_df = pandas.DataFrame(
    data=[
        {
            "expiration_date": c.expiration_date,
            "strike_price": c.strike_price,
            "symbol": c.symbol,
            "underlying_symbol": c.underlying_symbol,
            "close_price": c.close_price,
        }
        for c in option_contracts.option_contracts
    ],
)
latest_option_closes = get_puts_premiums_closes(options_df["symbol"].tolist())
option_closes_df = pandas.DataFrame(
    data=[
        {
            "conditions": c.conditions,
            "exchange": c.exchange,
            "price": c.price,
            "size": c.size,
            "symbol": c.symbol,
            "tape": c.tape,
            "timestamp": c.timestamp,
        }
        for c in latest_option_closes.values()
    ],
)
latest_option_asks = get_puts_premiums_asks(options_df["symbol"].tolist())
option_asks_df = pandas.DataFrame(
    data=[
        {
            "ask_exchange": c.ask_exchange,
            "ask_price": c.ask_price,
            "ask_size": c.ask_size,
            "conditions": c.conditions,
            "symbol": c.symbol,
            "tape": c.tape,
            "timestamp": c.timestamp,
        }
        for c in latest_option_asks.values()
    ],
)
