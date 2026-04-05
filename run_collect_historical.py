#
import os
import datetime

#
from dotenv import load_dotenv
from alpaca.data.timeframe import TimeFrame

#
from umbria_one.historical import alpaca as historical_broker, kraken as historical_crypto
from umbria_one.tech import connectors as conn

#
# run the collection process once

# 0) set up

load_dotenv()

ticker = "NVDA"
today = datetime.date.today()

ac = conn.get_alpaca_connector(
    api_key=os.environ.get("ALPACA_API_KEY"),
    secret_key=os.environ.get("ALPACA_USER_KEY"),
    paper=False,
)

# 1) collect the token price from crypto

crypto_historical_data, _, _ = historical_crypto.get_historical_token_ohlc(
    ticker=ticker,
    interval=60,
    # since=int(datetime.datetime(2023, 1, 1).timestamp()),
)

# 2) collect the market price from broker

broker_historical_data = historical_broker.get_historical_stock_ohlc(
    ac=ac,
    ticker=ticker,
    interval=TimeFrame.Hour,
    start_date=datetime.datetime(2026, 2, 27),
    end_date=datetime.datetime(2026, 3, 29),
)

# 3) collect the options from the broker

broker_historical_data = historical_broker.get_mass_load_option_dynamics(
    ac=ac,
    ticker=ticker,
    interval=TimeFrame.Hour,
    interval_datetime_delta=datetime.timedelta(hours=1),
    data_historical_stock_ohlc_df=broker_historical_data,
)

# 4) combine the data

joint_data = (
    crypto_historical_data
    .merge(
        right=broker_historical_data,
        left_index=True,
        right_index=True,
        how="outer",
        suffixes=("_crypto", "_broker"),
    )
)

joint_data["open_diff"] = (
    joint_data["open_crypto"] -
    joint_data["open_broker"]
)
joint_data["close_diff"] = (
    joint_data["close_crypto"] -
    joint_data["close_broker"]
)
joint_data["open_call_put_diff"] = (
    joint_data["call_option_open"] -
    joint_data["put_option_open"]
)
joint_data["close_call_put_diff"] = (
    joint_data["call_option_close"] -
    joint_data["put_option_close"]
)
joint_data["costs_plan_a"] = 0.40   # 0.10 0.25 0.40

joint_data["open_expected_result"] = (
    -joint_data["open_diff"]
    + joint_data["open_call_put_diff"]
    - joint_data["costs_plan_a"]
)
joint_data["close_expected_result"] = (
    -joint_data["close_diff"]
    + joint_data["close_call_put_diff"]
    - joint_data["costs_plan_a"]
)

joint_data["open_indicator_delta"] = (
    joint_data
    .apply(
        func=lambda x: 1 if x["open_diff"] <= -0.5 else 0,
        axis=1,
    )
)
joint_data["open_indicator_full"] = (
    joint_data
    .apply(
        func=lambda x: 1 if ((x["open_expected_result"] >= 0) and (x["open_diff"] <= -0.5)) else 0,
        axis=1,
    )
)
joint_data["close_indicator_delta"] = (
    joint_data
    .apply(
        func=lambda x: 1 if x["close_diff"] <= -0.5 else 0,
        axis=1,
    )
)
joint_data["close_indicator_full"] = (
    joint_data
    .apply(
        func=lambda x: 1 if ((x["close_expected_result"] >= 0) and (x["close_diff"] <= -0.5)) else 0,
        axis=1,
    )
)