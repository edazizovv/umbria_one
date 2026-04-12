from collections import deque
from threading import RLock
from .domain.models import MarketSnapshot, PortfolioSnapshot


class MarketStateCache:
    """In-memory cache for latest market and portfolio snapshots.
    
    This cache is designed for fast access to the most recent market and portfolio data.
    It also maintains a short history of snapshots for each source and symbol/account.
    """
    def __init__(
        self,
        market_history_size: int = 10,
        portfolio_history_size: int = 10,
    ):
        self._market_latest: dict[tuple[str, str], MarketSnapshot] = {}
        self._portfolio_latest: dict[tuple[str, str], PortfolioSnapshot] = {}

        self._market_history: dict[
            tuple[str, str], deque[MarketSnapshot]
        ] = {}

        self._portfolio_history: dict[
            tuple[str, str], deque[PortfolioSnapshot]
        ] = {}

        self._market_history_size = market_history_size
        self._portfolio_history_size = portfolio_history_size

        self._lock = RLock()

    # -------- MARKET --------

    def update_market_cache(self, snapshot: MarketSnapshot) -> None:
        key = (snapshot.source, snapshot.symbol)

        with self._lock:
            self._market_latest[key] = snapshot

            if key not in self._market_history:
                self._market_history[key] = deque(
                    maxlen=self._market_history_size
                )

            self._market_history[key].append(snapshot)

    def get_latest_market(
        self, source: str, symbol: str
    ) -> MarketSnapshot | None:
        return self._market_latest.get((source, symbol))

    def get_market_history(
        self, source: str, symbol: str
    ) -> list[MarketSnapshot]:
        return list(self._market_history.get((source, symbol), []))

    # -------- PORTFOLIO --------

    def update_portfolio_cache(self, snapshot: PortfolioSnapshot) -> None:
        key = (snapshot.source, snapshot.account_id)

        with self._lock:
            self._portfolio_latest[key] = snapshot

            if key not in self._portfolio_history:
                self._portfolio_history[key] = deque(
                    maxlen=self._portfolio_history_size
                )

            self._portfolio_history[key].append(snapshot)

    def get_latest_portfolio(self, source: str, account_id: str) -> PortfolioSnapshot | None:
        return self._portfolio_latest.get((source, account_id))

    def get_portfolio_history(self, source: str, account_id: str) -> list[PortfolioSnapshot]:
        return list(self._portfolio_history.get((source, account_id), []))
