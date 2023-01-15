import time
from datetime import datetime


def date_str_to_timestamp(date_str: str) -> int:
    """
    Args:
        date_str (str): A date string in the format YYYY-MM-DD
    
    Returns:
        int: a timestamp conversion of the given date string
    """
    return int(time.mktime(datetime.strptime(date_str, '%Y-%m-%d').timetuple()) * 1000)

def timeframe_to_ms(timeframe: str) -> int:
    """
    Args:
        timeframe (str): A string describing a timeframe. E.g. '1m', '15m', '1h', '7D'

    Returns:
        int: The length of the timeframe in milliseconds
    """
    units_of_time = {
        'm': 60_000,
        'h': 3_600_000,
        'D': 86_400_000,
        # TODO: Add weeks and months (requires more complex logic)
    }

    # Check that the timeframe is in the correct format
    try:
        length = int(timeframe[: -1])
    except:
        raise Exception(f'{length} is not a valid length of time')
    unit = timeframe[-1:]

    try:
        units_ms = units_of_time[unit]
    except:
        raise Exception(f'\'{timeframe}\' is not a valid unit of time')
    
    return int(length * units_ms)
