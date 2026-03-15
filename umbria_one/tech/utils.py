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
