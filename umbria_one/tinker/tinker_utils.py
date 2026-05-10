#
import uuid
import datetime

#
import pandas


#
from umbria_one.tinker.tinker_signals import calculate_signals
from umbria_one.dbio.dbio import get_live_scanner_df, save_live_signals, save_history_signals


#
async def update_signals(
    spread: float,
):

    live_signals_tab = "live_signals"
    historical_signals_tab = "historical_signals"
    sources = ["crypto", "broker"]
    strategy_code = "AAA"

    live_scanner_df = await get_live_scanner_df(
        sources=sources,
    )

    joint_df, joint_selected_df = await calculate_signals(
        live_scanner_df=live_scanner_df,
        spread=spread,
    )

    live_result = pandas.DataFrame(
        data={
            "strategy_code": [strategy_code],
            "signal_id": [str(uuid.uuid4())],
            "generated_at": [datetime.datetime.now(tz=datetime.UTC)],
            "parameters": [joint_selected_df.to_json()],
        }
    )
    await save_live_signals(
        df=live_result,
        table_name=live_signals_tab,
    )

    historical_result = pandas.DataFrame(
        data={
            "strategy_code": [strategy_code],
            "signal_id": [str(uuid.uuid4())],
            "generated_at": [datetime.datetime.now(tz=datetime.UTC)],
            "parameters": [joint_df.to_json()],
        }
    )
    await save_history_signals(
        df=historical_result,
        table_name=historical_signals_tab,
    )

    return
