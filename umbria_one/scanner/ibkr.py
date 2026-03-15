#
import datetime

#
from ib_insync import Stock, Option

#
from umbria_one.tech.utils import date_diff

#
def get_market_price(
    ib,
    ticker: str,
) -> float:
    """
    Retrieve market prices for a given ticker.

    :param ib: IBKR ??? connected instance
    :param ticker: ticker symbol
    :return: market price
    """

    stock = Stock(ticker, "SMART", "USD")
    ib.qualifyContracts(stock)
    ticker = ib.reqTickers(stock)[0]
    market_price = ticker.marketPrice()

    return market_price


def get_options(
    ib,
    ticker: str,
    reference_price: float,
    reference_date: str,
) -> dict:
    """
    Retrieve available options for a given ticker and market price.

    :param ib: IBKR ??? connected instance
    :param ticker: ticker symbol
    :param reference_price: reference price
    :param reference_date: reference date in YYYYMMDD format
    :return: options dictionary
    """

    options_dictionary = {}

    stock = Stock(ticker, "SMART", "USD")

    # 3. Get Available Put Options (Option Chain)
    chains = ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId)

    # Example: List puts for the nearest expiration
    chain = chains[0]  # Take the first exchange's chain

    # take the closest expiration that is not less than 4 days
    expiration = sorted(
        [
            x for x in chain.expirations
            if date_diff(
                older=reference_date,
                newer=x,
            ) >= datetime.timedelta(days=4)
        ]
    )[0]

    # take strikes that are closest to the reference price
    lower_strike = sorted([s for s in chain.strikes if s <= reference_price])[-1]
    upper_strike = sorted([s for s in chain.strikes if s >= reference_price])[0]
    if lower_strike == upper_strike:
        strikes = [lower_strike]
    else:
        strikes = [lower_strike, upper_strike]

    for strike in strikes:
        put_contract = Option(ticker, expiration, strike, 'P', 'SMART')
        ib.qualifyContracts(put_contract)
        put_ticker = ib.reqTickers(put_contract)[0]
        options_dictionary[ticker] = {
            "n_options": len(strikes),
            "expiration": expiration,
            "strike": strike,
            "price": put_ticker.last,
        }

    return options_dictionary
