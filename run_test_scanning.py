#
import os
import datetime

#
from dotenv import load_dotenv

#
from umbria_one.scanner import alpaca as scan_broker, kraken as scan_crypto
from umbria_one.tech import connectors as conn

#
# run the collection process once

# 0) set up

load_dotenv()

ticker = "AAPL"
today = datetime.date.today()

ac = conn.get_alpaca_connector(
    api_key=os.environ.get("ALPACA_API_KEY"),
    secret_key=os.environ.get("ALPACA_USER_KEY"),
    paper=False,
)

# 1) collect the token price from crypto

# token_price = scan_crypto.get_reference_price(
#     ticker=ticker,
# )

# 2) collect the market price from broker

market_price = scan_broker.get_market_price(
    ac=ac,
    ticker=ticker,
)

# 3) collect the options from broker

options = scan_broker.get_options(
    ac=ac,
    ticker=ticker,
    reference_price=market_price,     # should be token_price
    reference_date=today,
)
