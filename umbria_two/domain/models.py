from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal, Tuple

Side = Literal["buy", "sell"]
OrderStatus = Literal["new", "partially_filled", "filled", "cancelled", "rejected"]
SourceName = Literal["etoro", "kraken"]
PositionStatus = Literal["active", "order"]

@dataclass(frozen=True, slots=True)
class OrderBook:
    price: Decimal
    volume: Decimal

@dataclass(frozen=True, slots=True)
class OrderSnapshot:
    source: SourceName
    order_id: str

    symbol: str
    side: Side
    status: OrderStatus
    order_type: str
    price: Decimal | None
    quantity: Decimal
    filled_quantity: Decimal
    created_at: datetime
    updated_at: datetime
    raw: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class PortfolioSnapshot:
    source: SourceName
    account_id: str

    ts: datetime
    position_size: Decimal
    position_name: str
    position_funding: Decimal
    position_cost: Decimal
    position_status: PositionStatus
    raw: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class MarketSnapshot:
    source: SourceName
    symbol: str

    ts_exchange: datetime
    ts_ingested: datetime
    bids: Tuple[OrderBook, ...]
    asks: Tuple[OrderBook, ...]
    last: Decimal | None
    raw: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class SnapshotBundle:
    ts: datetime
    etoro: MarketSnapshot | None
    kraken: MarketSnapshot | None
    etoro_portfolio: PortfolioSnapshot | None = None
    kraken_portfolio: PortfolioSnapshot | None = None

@dataclass(frozen=True, slots=True)
class AnalysisResult:
    ts: datetime
    symbol: str
    mid_price: Decimal | None
    spread: Decimal | None
    volatility: Decimal | None
    features: dict[str, Any]


@dataclass(frozen=True, slots=True)
class StrategySignal:
    strategy_name: str
    symbol: str
    action: Action
    confidence: float
    reason: str


@dataclass(frozen=True, slots=True)
class Decision:
    symbol: str
    action: Action
    score: float
    reasons: list[str]
    ts: datetime
