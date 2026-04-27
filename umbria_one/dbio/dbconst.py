#
import os
import asyncio
import datetime

#
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import MetaData, Table, Column, String, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB

#


#
load_dotenv()

metadata = MetaData()

engine = create_async_engine(
    f"postgresql+asyncpg://"
    f"{os.environ.get('DB_USER')}:"
    f"{os.environ.get('DB_PASS')}@"
    f"{os.environ.get('DB_HOST')}/"
    f"{os.environ.get('DB_NAME')}"
)

live_scanner_tab = Table(
    'live_scanner', metadata,
    Column('source_id', String, primary_key=True),
    Column('entity_id', String, primary_key=True),
    Column('last_updated', DateTime(timezone=True)),
    Column('payload', JSONB)
)

historical_scanner_tab = Table(
    'historical_scanner', metadata,
    Column('source_id', String),
    Column('entity_id', String),
    Column('received_at', DateTime(timezone=True)),
    Column('payload', JSONB),
    Index('idx_history_source_entity_time', 'source_id', 'entity_id', 'received_at'),
)
