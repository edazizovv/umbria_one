#
import os
import datetime

#
from dotenv import load_dotenv

#
from umbria_one.tech import connectors as conn
from umbria_one.scanner import alpaca as scan_broker, kraken as scan_crypto

#
load_dotenv()

ticker = "AAPL"
today = datetime.date.today()

ac = conn.get_alpaca_connector(
    api_key=os.environ.get("ALPACA_API_KEY"),
    secret_key=os.environ.get("ALPACA_USER_KEY"),
    paper=False,
)

current_stock_order_book = scan_broker.get_stocks_lvl1_orderbook(
    ac=ac,
    ticker=ticker,
)

current_crypto_order_book = scan_crypto.get_token_lvl2_orderbook(
    ticker=ticker,
)
