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

    try:
        print(f"STOCK UPDATE: latest_bid={data.bid_price:.4f}; latest_ask={data.ask_price:.4f}")
    except Exception as e:
        print("ERROR:", e)


async def token_handler(data):

    try:
        data = {
            "latest_bid": data["bids"][0]["price"] if len(data["bids"]) > 0 else numpy.nan,
            "latest_ask": data["asks"][0]["price"] if len(data["asks"]) > 0 else numpy.nan,
        }

        print(f"TOKEN UPDATE: latest_bid={data['latest_bid']:.4f}; latest_ask={data['latest_ask']:.4f}")
    except Exception as e:
        print("ERROR:", e)


async def broker_portfolio_handler(positions):

    print("ptf handler")
    try:

        for p in positions:
            print(p.symbol, p.qty, p.market_value, p.unrealized_pl)

    except Exception as e:
        print("ERROR:", e)


async def broker_orders_handler(orders):

    print("ord handler")
    try:

        for o in orders:
            print(o.symbol, o.qty, o.filled_qty, o.status)

    except Exception as e:
        print("ERROR:", e)


async def main():
    print("Starting...")
    await asyncio.gather(
        scan_broker.get_websockets_stocks_lvl1_orderbook_stream(
            ac=ac,
            ticker=ticker,
            stream_handler=stock_handler,
        ),
        # scan_broker.get_rest_portfolio_state(
        #     ac=ac,
        #     stream_handler=broker_portfolio_handler,
        # ),
        # scan_broker.get_rest_current_orders(
        #     ac=ac,
        #     stream_handler=broker_orders_handler,
        # ),
        # scan_crypto.get_websockets_token_lvl2_orderbook_stream(
        #     ticker=ticker,
        #     stream_handler=token_handler,
        # ),
    )

if __name__ == "__main__":
    asyncio.run(main())
