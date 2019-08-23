import logging

import requests
from requests.exceptions import ConnectionError


def live_check_unsafe(endpoint: str, logger: logging.Logger) -> None:
    # This throws a ConnectionError if the live check fails
    head_ret = requests.head(endpoint, timeout=10)
    logger.debug('live_check: head_ret: %s', head_ret)


def live_check(endpoint: str, logger: logging.Logger) -> bool:
    try:
        live_check_unsafe(endpoint, logger)
        return True
    except ConnectionError:
        return False
