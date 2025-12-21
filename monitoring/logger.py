""" To be replaced.. """

from pathlib import Path
import datetime as dt


def server_error_logger(error_code, error_message):
    """ Simple temp func for logging server errors. To eb replaced with logging """

    data = {
        "date": dt.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "operation": "X", # yet to implement
        "error_code": error_code,
        "error_message": error_message
    }

    write_error_to_log(data)


def write_error_to_log(data):
    """ Temp func to write to log, refactor later cleanly using proper DB. """

    filepath = Path('storage/error_logs.txt')
    filepath.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    
    with filepath.open(mode="a", encoding="utf-8") as f:
        f.write(str(data))
        f.write('\n')