#


#
import pandas

#


#
async def calculate_signals(
    live_scanner_df,
    spread: float,
):

    live_scanner_crypto_df = live_scanner_df[
        live_scanner_df["source_id"] == "crypto"
    ].copy()
    live_scanner_broker_df = live_scanner_df[
        live_scanner_df["source_id"] == "broker"
    ].copy()

    live_scanner_crypto_bids_df = pandas.DataFrame([
        {**bid, 'entity_id': row.entity_id}
        for row in live_scanner_crypto_df.itertuples()
        for bid in row.payload.get('bids', [])
    ]).rename(columns={
        "price": "crypto_bid_price",
        "qty": "crypto_bid_amount",
    }).sort_values(
        by=["entity_id", "crypto_bid_price"],
        ascending=[True, False],
    )
    live_scanner_crypto_bids_df["amount"] = (
        live_scanner_crypto_bids_df
        .groupby(
            "entity_id"
        )
        ["crypto_bid_amount"]
        .cumsum()
    )

    live_scanner_crypto_asks_df = pandas.DataFrame([
        {**ask, 'entity_id': row.entity_id}
        for row in live_scanner_crypto_df.itertuples()
        for ask in row.payload.get('asks', [])
    ]).rename(columns={
        "price": "crypto_ask_price",
        "qty": "crypto_ask_amount",
    }).sort_values(
        by=["entity_id", "crypto_ask_price"],
        ascending=[True, True],
    )
    live_scanner_crypto_asks_df["amount"] = (
        live_scanner_crypto_asks_df
        .groupby(
            "entity_id"
        )
        ["crypto_ask_amount"]
        .cumsum()
    )

    live_scanner_broker_bids_df = pandas.json_normalize(
        live_scanner_broker_df['payload']
    ).rename(columns={
        "bid_price": "broker_bid_price",
        "bid_size": "broker_bid_amount",
    }).sort_values(
        by=["entity_id", "broker_bid_price"],
        ascending=[True, False],
    )
    live_scanner_broker_bids_df["amount"] = (
        live_scanner_broker_bids_df
        .groupby(
            "entity_id"
        )
        ["broker_bid_amount"]
        .cumsum()
    )
    live_scanner_broker_asks_df = pandas.json_normalize(
        live_scanner_broker_df['payload']
    ).rename(columns={
        "ask_price": "broker_ask_price",
        "ask_size": "broker_ask_amount",
    }).sort_values(
        by=["entity_id", "broker_ask_price"],
        ascending=[True, True],
    )
    live_scanner_broker_asks_df["amount"] = (
        live_scanner_broker_asks_df
        .groupby(
            "entity_id"
        )
        ["broker_ask_amount"]
        .cumsum()
    )

    joint_df = (
        live_scanner_crypto_bids_df
        .merge(
            right=live_scanner_crypto_asks_df,
            left_on=["entity_id", "amount"],
            right_on=["entity_id", "amount"],
            how="outer",
        )
        .merge(
            right=live_scanner_broker_bids_df,
            left_on=["entity_id", "amount"],
            right_on=["entity_id", "amount"],
            how="outer",
        )
        .merge(
            right=live_scanner_broker_asks_df,
            left_on=["entity_id", "amount"],
            right_on=["entity_id", "amount"],
            how="outer",
        )
        .sort_values(
            by=["entity_id", "amount"],
            asending=[True, True],
        )
    )

    joint_df[
        [
            "crypto_bid_price",
            "crypto_ask_price",
            "broker_bid_price",
            "broker_ask_price",
        ]
    ] = (
        joint_df
        .groupby(
            "entity_id"
        )
        [
            [
                "crypto_bid_price",
                "crypto_ask_price",
                "broker_bid_price",
                "broker_ask_price",
            ]
        ]
        .bfill()
    )

    joint_df["crypto_mid_price"] = (
        (
                joint_df["crypto_bid_price"]
                + joint_df["crypto_ask_price"]
        ) / 2
    )

    joint_df["broker_mid_price"] = (
        (
                joint_df["broker_bid_price"]
                + joint_df["broker_ask_price"]
        ) / 2
    )

    joint_df["theoretical_spread"] = (
        joint_df["broker_mid_price"]
        - joint_df["crypto_mid_price"]
    )

    joint_df["bidask_fee"] = (
        joint_df["crypto_ask_price"]
        - joint_df["crypto_bid_price"]
        + joint_df["broker_ask_price"]
        - joint_df["broker_bid_price"]
    )

    joint_df["estimated_spread"] = (
        joint_df["theoretical_spread"]
        - joint_df["bidask_fee"]
    )

    joint_selected_df = joint_df[
        joint_df["estimated_spread"] >= spread
    ]

    joint_selected_df = joint_selected_df[
        joint_selected_df
        .groupby(
            "entity_id"
        )
        ["amount"]
        .idxmax()
    ].copy()

    return joint_df, joint_selected_df
