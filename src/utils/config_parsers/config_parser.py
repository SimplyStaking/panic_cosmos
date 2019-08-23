import os
from typing import List

from src.utils.exceptions import ConfigNotFoundException


class ConfigParser:

    def __init__(self, config_file_paths: List[str]) -> None:
        for path in config_file_paths:
            if not os.path.isfile(path):
                raise ConfigNotFoundException(path)
