#
import os
import json
import asyncio
import datetime
from functools import partial

#
from dotenv import load_dotenv

#
from umbria_one.tech import connectors as conn
from umbria_one.scanner import alpaca as scan_broker, kraken as scan_crypto
from umbria_one.dbio.dbio import update_live_scanner_tab
from umbria_one.dbio.dbutils import history_worker, CurrentData

#
load_dotenv()

ticker = "AAPL"
today = datetime.date.today()

ac = conn.get_alpaca_connector(
    api_key=os.environ.get("ALPACA_API_KEY"),
    secret_key=os.environ.get("ALPACA_USER_KEY"),
    paper=False,
)

async def broker_handler(data, ticker, history_queue):

    print(f"loading broker {ticker}...")
    data = json.loads(data.model_dump_json())
    data = {
        "source_id": "broker",
        "entity_id": ticker,
        "last_updated": datetime.datetime.now(datetime.UTC).isoformat(),
        "payload": data,
    }

    try:
        # await update_live_scanner_tab(
        #     data=data,
        # )

        await history_queue.put(data)

        print(f"Queue size: {history_queue.qsize()}")

    except Exception as e:
        print("ERROR:", e)


async def crypto_handler(data, ticker, history_queue, current_data):

    print(f"loading crypto {ticker}...")
    data = {
        "source_id": "crypto",
        "entity_id": ticker,
        "last_updated": datetime.datetime.now(datetime.UTC).isoformat(),
        "payload": data,
    }

    try:
        # await update_live_scanner_tab(
        #     data=data,
        # )

        if data["payload"]["type"] == "update":
            if len(data["payload"]["asks"]) == 0:
                data["payload"]["asks"] = current_data["asks"]
            else:
                current_data["asks"] = data["payload"]["asks"]
            if len(data["payload"]["bids"]) == 0:
                data["payload"]["bids"] = current_data["bids"]
            else:
                current_data["bids"] = data["payload"]["bids"]
        else:
            current_data.update(data["payload"])

        await history_queue.put(data)

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

    history_queue = asyncio.Queue()

    current_data = CurrentData()

    worker_task = asyncio.create_task(history_worker(
        history_queue=history_queue,
    ))

    bound_broker_handler = partial(broker_handler, history_queue=history_queue)
    bound_crypto_handler = partial(crypto_handler, history_queue=history_queue, current_data=current_data)

    try:
        await asyncio.gather(
            # scan_broker.get_websockets_stocks_lvl1_orderbook_stream(
            #     ac=ac,
            #     ticker=ticker,
            #     stream_handler=bound_broker_handler,
            # ),
            # scan_broker.get_rest_portfolio_state(
            #     ac=ac,
            #     stream_handler=broker_portfolio_handler,
            # ),
            # scan_broker.get_rest_current_orders(
            #     ac=ac,
            #     stream_handler=broker_orders_handler,
            # ),
            scan_crypto.get_websockets_token_lvl2_orderbook_stream(
                ticker=ticker,
                stream_handler=bound_crypto_handler,
            ),
        )
    finally:
        worker_task.cancel()
        await asyncio.gather(worker_task, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())
