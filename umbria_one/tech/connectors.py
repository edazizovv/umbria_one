#


#
# from ib_insync import IB
from alpaca.data.historical import StockHistoricalDataClient, OptionHistoricalDataClient
from alpaca.trading.client import TradingClient

#


#
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
