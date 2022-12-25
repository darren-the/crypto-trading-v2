import time
from datetime import datetime


def date_str_to_timestamp(date_str: str) -> int:
    """
    Args:
        date_str (str): A date string in the format YYYY-MM-DD
    
    Returns:
        int: a timestamp conversion of the given date string
    """
    return time.mktime(datetime.strptime(date_str, '%Y-%m-%d').timetuple()) * 1000