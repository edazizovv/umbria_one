#
import os
import asyncio
import datetime

#
import numpy
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

async def stock_handler(data):

    print(f"STOCK UPDATE: latest_bid={data['stock_bid']:.4f}; latest_ask={data['stock_ask']:.4f}")


async def token_handler(data):

    data = {
        "latest_bid": data["bids"][0]["price"] if len(data["bids"]) > 0 else numpy.nan,
        "latest_ask": data["asks"][0]["price"] if len(data["asks"]) > 0 else numpy.nan,
    }

    print(f"TOKEN UPDATE: latest_bid={data['latest_bid']:.4f}; latest_ask={data['latest_ask']:.4f}")


async def main():
    print("Starting...")
    await asyncio.gather(
        scan_broker.get_websockets_stocks_lvl1_orderbook_stream(
            ac=ac,
            ticker=ticker,
            stream_handler=stock_handler,
        ),
        # scan_crypto.get_websockets_token_lvl2_orderbook_stream(
        #     ticker=ticker,
        #     stream_handler=token_handler,
        # ),
    )

if __name__ == "__main__":
    asyncio.run(main())
