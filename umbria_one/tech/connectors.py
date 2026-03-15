#


#


#


#
def get_ibkr_connector(
    ibkr_ip: str,
    ibkr_port: int,
    ibkr_client_id: int,
) -> IB:
    """

    :param ibkr_ip: ???
    :param ibkr_port: ???
    :param ibkr_client_id: ???
    :return: IBKR ??? connected instance
    """

    ib = IB()
    ib.connect(ibkr_ip, ibkr_port, clientId=ibkr_client_id)

    return ib
