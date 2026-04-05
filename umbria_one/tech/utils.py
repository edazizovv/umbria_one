#
import datetime

#

#


#
def date_diff(
    older: str,
    newer: str,
) -> datetime.timedelta:
    """
    Calculate timedelta between two str dates

    :param older: date in YYYYMMDD format
    :param newer: date in YYYYMMDD format
    :return: timedelta
    """

    older_date = datetime.date.strptime(older, "%Y%m%d")
    newer_date = datetime.date.strptime(newer, "%Y%m%d")

    result = newer_date - older_date

    return result


def strike_step_heuristic(spot):
    if spot < 50:
        return 1
    elif spot < 150:
        return 2.5
    else:
        return 5


def build_option_symbol(underlying: str, expiration, strike: float, option_type: str) -> str:
    """
    Build OCC/Alpaca option symbol.

    Parameters
    ----------
    underlying : str
        e.g. "AAPL"
    expiration : datetime or str
        e.g. datetime(2022, 1, 21) or "2022-01-21"
    strike : float
        e.g. 170.0
    option_type : str
        "C" for call, "P" for put

    Returns
    -------
    str
        e.g. "AAPL220121C00170000"
    """

    # --- normalize expiration ---
    if isinstance(expiration, str):
        expiration = datetime.datetime.fromisoformat(expiration)

    exp_str = expiration.strftime("%y%m%d")

    # --- normalize option type ---
    option_type = option_type.upper()
    if option_type not in ["C", "P"]:
        raise ValueError("option_type must be 'C' or 'P'")

    # --- format strike ---
    # OCC format: strike * 1000, zero-padded to 8 digits
    strike_int = int(round(strike * 1000))
    strike_str = f"{strike_int:08d}"

    return f"{underlying.upper()}{exp_str}{option_type}{strike_str}"
