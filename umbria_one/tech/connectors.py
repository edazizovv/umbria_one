#
import uuid

#
# from ib_insync import IB
from alpaca.data.historical import StockHistoricalDataClient, OptionHistoricalDataClient
from alpaca.data.live import StockDataStream
from alpaca.trading.client import TradingClient

#


#
class EtoroConnector:
    def __init__(
        self,
        api_key: str,
        secret_key: str,
    ):
        self.base_url = "https://public-api.etoro.com/api/v1"
        self.headers = {
            "x-api-key": f"{api_key}",
            "x-user-key": f"{secret_key}",
            "x-request-id": str(uuid.uuid4()),  # Required for tracking requests
            "Content-Type": "application/json"
        }


def get_etoro_connector(
    api_key: str,
    secret_key: str,
) -> EtoroConnector:

    ec = EtoroConnector(api_key, secret_key)

    return ec


def get_ibkr_connector(
    ibkr_ip: str,
    ibkr_port: int,
    ibkr_client_id: int,
) -> IB:
    """
    Create IBKR connector

    :param ibkr_ip: ???
    :param ibkr_port: ???
    :param ibkr_client_id: ???
    :return: IBKR ??? connected instance
    """

    ib = IB()
    ib.connect(ibkr_ip, ibkr_port, clientId=ibkr_client_id)

    return ib


class AlpacaConnectorData:
    def __init__(
        self,
        api_key: str,
        secret_key: str,
    ) -> None:
        self.stocks = StockHistoricalDataClient(api_key, secret_key)
        self.options = OptionHistoricalDataClient(api_key, secret_key)


class AlpacaConnector:
    def __init__(
        self,
        api_key: str,
        secret_key: str,
        paper: bool,
    ) -> None:
        self.data = AlpacaConnectorData(api_key=api_key, secret_key=secret_key)
        self.trading = TradingClient(api_key, secret_key, paper=paper)
        self.data_live = StockDataStream(api_key=api_key, secret_key=secret_key)


def get_alpaca_connector(
    api_key: str,
    secret_key: str,
    paper: bool,
) -> AlpacaConnector:
    """
    Create alpaca connector

    :param api_key: API key
    :param secret_key: Secret key
    :param paper: Whether paper trading is used
    :return: alpaca connector
    """

    ac = AlpacaConnector(api_key, secret_key, paper=paper)

    return ac
