import json
import logging
import os
from typing import Dict, Union

import requests


def get_json(endpoint: str, logger: logging.Logger,
             verify: Union[str, bool] = True) -> Dict:
    get_ret = requests.get(endpoint, timeout=10, verify=verify)
    logger.debug('get_json: get_ret: %s', get_ret)
    return json.loads(get_ret.content.decode('UTF-8'))


def get_cosmos_json_raw(endpoint: str, logger: logging.Logger) -> Dict:
    if os.path.isfile("cert.pem"):
        return get_json(endpoint, logger, verify="cert.pem")
    else:
        return get_json(endpoint, logger)


def get_cosmos_json(endpoint: str, logger: logging.Logger) -> Dict:
    return get_cosmos_json_raw(endpoint, logger)['result']
