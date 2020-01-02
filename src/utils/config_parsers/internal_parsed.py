import os

from src.utils.config_parsers.internal import InternalConfig

INTERNAL_CONFIG_FILE = 'config/internal_config.ini'
INTERNAL_CONFIG_FILE_FOUND = os.path.isfile(INTERNAL_CONFIG_FILE)

if INTERNAL_CONFIG_FILE_FOUND:
    InternalConf = InternalConfig(INTERNAL_CONFIG_FILE)
else:
    InternalConf = None
