import json
import logging
from typing import Dict

import requests


def get_json(endpoint: str, logger: logging.Logger) -> Dict:
    get_ret = requests.get(endpoint, timeout=10)
    logger.debug('get_json: get_ret: %s', get_ret)
    return json.loads(get_ret.content.decode('UTF-8'))


def get_cosmos_json(endpoint: str, logger: logging.Logger) -> Dict:
    return get_json(endpoint, logger)['result']
