#
import datetime


#
import pandas
from sqlalchemy import text, select
from sqlalchemy.dialects.postgresql import insert


#
from umbria_one.dbio.dbconst import engine, live_scanner_tab, historical_scanner_tab


#
async def get_live_scanner_df(
    sources,
):

    stmt = (
        select(
            live_scanner_tab
        )
        .where(
            live_scanner_tab.c.source_id.in_(sources)
        )
    )

    async with engine.connect() as conn:
        result = await conn.execute(stmt)

        # _mapping converts rows to dicts; list() creates the collection for Pandas
        data = [row._mapping for row in result.all()]

        if not data:
            return pandas.DataFrame()

        return pandas.DataFrame(data)


async def save_history_signals(
    df,
    table_name,
):

    if df.empty:

        return

    async with engine.begin() as conn:

        await conn.run_sync(
            lambda sync_conn: df.to_sql(
                name=table_name,
                con=sync_conn,
                if_exists='append',
                index=False,
                method='multi',
            )
        )
    print(f"Signals table {table_name} updated with {len(df)} fresh rows.")


async def save_live_signals(
    df,
    table_name,
):

    if df.empty:

        async with engine.begin() as conn:
            await conn.execute(text(f"TRUNCATE TABLE {table_name}"))
        return

    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE TABLE {table_name}"))

        await conn.run_sync(
            lambda sync_conn: df.to_sql(
                name=table_name,
                con=sync_conn,
                if_exists='append',
                index=False,
                method='multi',
            )
        )
    print(f"Signals table {table_name} updated with {len(df)} fresh rows.")


async def save_live_and_history_batch(batch):

    async with engine.begin() as conn:
        await conn.execute(
            historical_scanner_tab.insert(),
            batch,
        )

        latest_items = {(item["source_id"], item["entity_id"]): item for item in batch}

        for entity_id, data in latest_items.items():

            await update_live_scanner_tab(data=data, conn=conn)

    print(f"Flushed {len(batch)} records to history.")


async def update_live_scanner_tab(
    data,
    conn,
):
    """

    :param source:
    :param entity:
    :param data:
    :return:
    """

    data["last_updated"] = datetime.datetime.fromisoformat(data["last_updated"].replace("Z", "+00:00"))

    statement = (
        insert(
            live_scanner_tab
        )
        .values(
            data
        )
    )

    upsert_statement = (
        statement
        .on_conflict_do_update(
            index_elements=[
                "source_id",
                "entity_id",
            ],
            set_={
                "payload": statement.excluded.payload,
                "last_updated": statement.excluded.last_updated,
            }
        )
    )

    await conn.execute(upsert_statement)


def update_hist_scanner_tab(

):
    ...


def update_live_orders_tab(

):
    ...


def update_hist_orders_tab(

):
    ...


def update_live_ptf_tab(

):
    ...


def update_hist_ptf_tab(

):
    ...


def update_live_signals_tab(

):
    ...

def update_hist_signals_tab(

):
    ...
