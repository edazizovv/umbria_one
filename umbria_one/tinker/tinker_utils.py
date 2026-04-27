#


#
from sqlalchemy import select


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

    live_scanner_df = await get_live_scanner_df(
        sources=sources,
    )

    joint_df, joint_selected_df = await calculate_signals(
        live_scanner_df=live_scanner_df,
        spread=spread,
    )

    await save_live_signals(
        df=joint_selected_df,
        table_name=live_signals_tab,
    )

    await save_history_signals(
        df=joint_df,
        table_name=historical_signals_tab,
    )

    return
