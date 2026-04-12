from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

class MarketDataSource(ABC):

    @abstractmethod
    async def subscribe(self) -> AsyncIterator[MarketSnapshot]:
        """Stream real-time market data."""
        pass

    @abstractmethod
    async def get_latest_portfolio(self) -> PortfolioSnapshot:
        pass

    @abstractmethod
    async def get_open_orders(self) -> list[OrderSnapshot]:
        pass


class SnapshotRepository(ABC):

    @abstractmethod
    async def save_market_snapshot(self, snapshot: MarketSnapshot) -> None:
        pass

    @abstractmethod
    async def save_portfolio_snapshot(self, snapshot: PortfolioSnapshot) -> None:
        pass

    @abstractmethod
    async def save_order_snapshot(self, snapshot: OrderSnapshot) -> None:
        pass

    @abstractmethod
    async def get_latest_market(self, source: str, symbol: str) -> MarketSnapshot | None:
        pass