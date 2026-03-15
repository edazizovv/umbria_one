#
import datetime

#


#
from umbria_one.scanner import ibkr as scan_ibkr, kraken as scan_kraken
from umbria_one.tech import connectors as conn

#
# run the collection process once

# 0) set up

ticker = "AAPL"
today = datetime.date.today().strftime(format="%Y%m%d")

ib = conn.get_ibkr_connector(
    ibkr_ip="127.0.0.1",
    ibkr_port=7497,
    ibkr_client_id=1,
)

# 1) collect the token price from kraken

token_price = scan_kraken.get_reference_price(
    ticker=ticker,
)

# 2) collect the market price from ibkr

market_price = scan_ibkr.get_market_price(
    ib=ib,
    ticker=ticker,
)

# 3) collect the options from ibkr

options = scan_ibkr.get_options(
    ib=ib,
    ticker=ticker,
    reference_price=token_price,
    reference_date=today,
)
